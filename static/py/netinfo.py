#!/usr/bin/env python3

import argparse
import json
import logging
import os
import queue
import signal
import sys
import threading
import time

from netmiko import ConnectHandler

from netbrain import NetBrain

logging.basicConfig(level=logging.WARNING)

cwd = os.getcwd()
results = dict()
results_queue = queue.Queue()
router_types = ["Cisco", "Palo Alto Networks"]


def sigint_handler(signum, frame):
    sys.exit(1)


def import_env(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return None


def get_active_gateway(nb, src_ip):
    """Get the active gateway for the source subnet"""
    for gw in nb.get_gateway_list(src_ip):
        gw = json.loads(gw["payload"])

        # Skip if no device key
        if device := gw.get("device"):
            # Strip firewall vsys from hostname
            if "/" in device:
                device = device.split("/")[0]

            device_attrs = nb.get_device_attrs(device)
        else:
            continue

        # Skip unknown routing devices
        if device_attrs["vendor"] not in router_types:
            device_attrs = ""
            continue

        # Skip PAN HA passive member
        if device_attrs["vendor"] == "Palo Alto Networks" and device_attrs["isHA"]:
            if nb.get_pan_ha_state(device_attrs["name"]) == "passive":
                continue

        device_attrs.update({"srcIP": gw["ip"]})

        return device_attrs


def parse_args():
    parser = argparse.ArgumentParser(
        description="Trace route from source to destination"
    )
    parser.add_argument(
        "-s", "--source", metavar="", type=str, required=True, help="Source IP address"
    )
    parser.add_argument(
        "-d",
        "--destination",
        metavar="",
        type=str,
        required=True,
        help="Destination IP address",
    )

    return parser.parse_args()


def analyze_path(mgmt_ip, src_ip, dst_ip, credentials, vendor):
    """Analyze the path between the source and destination"""

    vendors = {
        "Cisco": {
            "ssh": {
                "device_type": "cisco_ios",
                "host": mgmt_ip,
                "username": credentials["Cisco"]["username"],
                "password": credentials["Cisco"]["password"],
            },
            "ttp_template": fr"{cwd}\cisco.ttp",
            "commands": [
                f"ping {dst_ip} source {src_ip}",
                f"traceroute {dst_ip} source {src_ip}",
            ],
        },
        "Palo Alto Networks": {
            "ssh": {
                "device_type": "paloalto_panos",
                "host": mgmt_ip,
                "username": credentials["Palo Alto Networks"]["username"],
                "password": credentials["Palo Alto Networks"]["password"],
            },
            "ttp_template": fr"{cwd}\pan.ttp",
            "commands": [
                f"ping count 4 source {src_ip} host {dst_ip}",
                f"traceroute source {src_ip} host {dst_ip}",
            ],
        },
    }

    output = list()
    with ConnectHandler(**vendors[vendor]["ssh"]) as net_connect:
        for cmd in vendors[vendor]["commands"]:
            output.append(
                net_connect.send_command_timing(
                    cmd,
                    strip_prompt=True,
                    strip_command=True,
                    delay_factor=2,
                    use_ttp=False,
                    ttp_template=vendors[vendor]["ttp_template"],
                )
            )

    return output


def worker(nb, src, dst, credentials, direction):
    device_attrs = get_active_gateway(nb, src)
    logging.info(json.dumps(device_attrs, indent=2, sort_keys=True))

    results = analyze_path(
        device_attrs["mgmtIP"],
        device_attrs["srcIP"],
        dst,
        credentials,
        device_attrs["vendor"],
    )

    results_queue.put({direction: results})


def results_manager():
    global results

    while True:
        result = results_queue.get()
        results.update(result)
        results_queue.task_done()


def main():
    t1_start = time.time()

    # Ctrl+C graceful exit
    signal.signal(signal.SIGINT, sigint_handler)

    args = parse_args()

    env = import_env("static/py/env.json")
    nb = NetBrain(
        env["netbrain_url"],
        env["netbrain_user"],
        env["netbrain_password"],
        env["tenant_name"],
        env["domain_name"],
    )

    # Results manager
    t = threading.Thread(target=results_manager)
    t.daemon = True
    t.start()
    del t

    # Bidirectional path analysis
    worker_threads = []
    for src, dst in [(args.source, args.destination), (args.destination, args.source)]:
        direction = "forward" if src == args.source else "reverse"
        t = threading.Thread(
            target=worker, args=(nb, src, dst, env["credentials"], direction)
        )
        worker_threads.append(t)
        t.start()

    for t in worker_threads:
        t.join()

    results_queue.join()

    print("\n".join(results["forward"]))
    print("\n".join(results["reverse"]))

    t1_stop = time.time()
    print(f"\n Took {t1_stop-t1_start :.3f} seconds to complete")


if __name__ == "__main__":
    main()
