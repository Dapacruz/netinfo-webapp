#!/usr/bin/env python3.8

# TODO: Insert hop zero (router source IP / client default gateway)
# TODO: Parse traceroute output
# TODO: Stylize web frontend

import argparse
import json
import logging
import os
import queue
import re
import signal
import sys
import threading
import time

from netbrain import NetBrain
from netmiko import ConnectHandler

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
    device_attrs = {}

    for gw in nb.get_gateway_list(src_ip):
        gw = json.loads(gw["payload"])

        # Skip if no device key
        device = gw.get("device")
        if device:
            # Strip firewall vsys from hostname
            if "/" in device:
                device = device.split("/")[0]

            device_attrs = nb.get_device_attrs(device)
        else:
            continue

        # Skip unknown routing devices
        if device_attrs["vendor"] not in router_types:
            device_attrs = {}
            continue

        # Skip PAN HA passive member
        if device_attrs["vendor"] == "Palo Alto Networks" and device_attrs["isHA"]:
            if nb.get_pan_ha_state(device_attrs["name"]) == "passive":
                device_attrs = {}
                continue

        device_attrs.update({"srcIP": gw["ip"]})

        return device_attrs

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


def parse_ping(vendor, data):
    results = {
        "sent": "N/A",
        "received": "N/A",
        "min": "N/A",
        "avg": "N/A",
        "max": "N/A",
        "mdev": "N/A",
    }
    if vendor == "Palo Alto Networks":
        rx = re.findall(r"(\d)\spackets transmitted,\s(\d)\sreceived", data)
        if rx:
            results.update(
                {
                    "sent": int(rx[0][0]),
                    "received": int(rx[0][1]),
                }
            )

        rtt = re.findall(r"rtt.*?([.\d]+)/([.\d]+)/([.\d]+)/([.\d]+)", data)
        if rtt:
            results.update(
                {
                    "min": float(rtt[0][0]),
                    "avg": float(rtt[0][1]),
                    "max": float(rtt[0][2]),
                    "mdev": float(rtt[0][3]),
                }
            )
    elif vendor == "Cisco Nexus":
        rx = re.findall(r"(\d)\spackets transmitted,\s(\d)\spackets", data)
        if rx:
            results.update(
                {
                    "sent": int(rx[0][0]),
                    "received": int(rx[0][1]),
                }
            )
        rtt = re.findall(r"round-trip.*?([.\d]+)/([.\d]+)/([.\d]+)", data)
        if rtt:

            results.update(
                {
                    "min": float(rtt[0][0]),
                    "avg": float(rtt[0][1]),
                    "max": float(rtt[0][2]),
                }
            )
    elif vendor == "Cisco":
        rtt = re.findall(
            r"Success.*?(\d{1,3})\spercent\s\((\d)/(\d).*?([.\d]+)/([.\d]+)/([.\d]+)",
            data,
        )
        if rtt:
            results.update(
                {
                    "sent": int(rtt[0][2]),
                    "received": int(rtt[0][1]),
                    "min": float(rtt[0][3]),
                    "avg": float(rtt[0][4]),
                    "max": float(rtt[0][5]),
                }
            )
    else:
        return None

    return results


def parse_traceroute(vendor, gw_name, gw_src, data):
    results = ""
    if vendor == "Palo Alto Networks":
        results = re.sub(
            r"(traceroute\sto.*)",
            rf"\1\n 0  {gw_name.lower()}.wsgc.com ({gw_src})",
            data,
        )
        # Remove empty first line
        results = "\n".join(results.split("\n")[1:])
    elif vendor == "Cisco Nexus":
        results = re.sub(
            r"(traceroute.*)",
            rf"\n\1",
            data,
        )
        results = re.sub(
            r"(\s1\s{2}\d{1,3}\..*ms)",
            rf" 0  {gw_name.lower()}.wsgc.com ({gw_src})\n\1",
            results,
        )
    elif vendor == "Cisco":
        results = re.sub(
            r"(\s{2}1\s\d{1,3}\..*msec)",
            rf"  0 {gw_name.lower()}.wsgc.com ({gw_src})\n\1",
            data,
        )
    else:
        return None

    return results


def analyze_path(
    gw_name, mgmt_ip, gw_src, src, dst, device_user, device_pw, vendor, model
):
    """Analyze the path between the source and destination"""

    if vendor == "Cisco" and "Nexus" in model:
        vendor = "Cisco Nexus"

    vendors = {
        "Palo Alto Networks": {
            "ssh": {
                "device_type": "paloalto_panos",
                "host": mgmt_ip,
                "username": device_user,
                "password": device_pw,
                "conn_timeout": 60,
            },
            "expect_string": r">",
            "commands": {
                "ping_src": f"ping count 3 source {gw_src} host {src}",
                "ping_dst": f"ping count 3 source {gw_src} host {dst}",
                "traceroute": f"traceroute wait 1 max-ttl 15 source {gw_src} host {dst}",
            },
        },
        "Cisco Nexus": {
            "ssh": {
                "device_type": "cisco_nxos",
                "host": mgmt_ip,
                "username": device_user,
                "password": device_pw,
                "conn_timeout": 60,
            },
            "expect_string": r"#|(\s\d{1,2}\s{2}\*\s\*\s\*\s*){5}",
            "commands": {
                "ping_src": f"ping {src} source {gw_src} timeout 1 count 3",
                "ping_dst": f"ping {dst} source {gw_src} timeout 1 count 3",
                "traceroute": f"traceroute {dst} source {gw_src}",
            },
        },
        "Cisco": {
            "ssh": {
                "device_type": "cisco_ios",
                "host": mgmt_ip,
                "username": device_user,
                "password": device_pw,
                "conn_timeout": 60,
            },
            "expect_string": r"#",
            "commands": {
                "ping_src": f"ping {src} source {gw_src} timeout 1 repeat 3",
                "ping_dst": f"ping {dst} source {gw_src} timeout 1 repeat 3",
                "traceroute": f"traceroute {dst} source {gw_src} timeout 1 ttl 0 15",
            },
        },
    }

    output = dict()
    with ConnectHandler(**vendors[vendor]["ssh"]) as net_connect:
        for k, cmd in vendors[vendor]["commands"].items():
            results = net_connect.send_command(
                cmd,
                strip_prompt=True,
                strip_command=True,
                max_loops=50000,
                expect_string=vendors[vendor]["expect_string"],
            )

            if k.startswith("ping"):
                ping_dst = src if k == "ping_src" else dst
                results_parsed = {
                    "gateway": gw_name,
                    "source": gw_src,
                    "destination": ping_dst,
                }
                results_parsed.update(parse_ping(vendor, results))
                output[k] = results_parsed
            else:
                output[k] = parse_traceroute(vendor, gw_name, gw_src, results)
    return output


def worker(nb, src, dst, device_user, device_pw, direction):
    gw_attrs = get_active_gateway(nb, src)
    logging.info(json.dumps(gw_attrs, indent=2, sort_keys=True))

    if gw_attrs:
        results = analyze_path(
            gw_attrs.get("name"),
            gw_attrs.get("mgmtIP"),
            gw_attrs.get("srcIP"),
            src,
            dst,
            device_user,
            device_pw,
            gw_attrs.get("vendor"),
            gw_attrs.get("model"),
        )

        results_queue.put({direction: results})
    else:
        results_queue.put(
            {
                direction: {
                    "ping_src": {
                        "gateway": "Gateway not implemented",
                        "source": "",
                        "destination": "",
                        "sent": "",
                        "received": "",
                        "min": "",
                        "avg": "",
                        "max": "",
                        "mdev": "",
                    },
                    "ping_dst": {
                        "gateway": "Gateway not implemented",
                        "source": "",
                        "destination": "",
                        "sent": "",
                        "received": "",
                        "min": "",
                        "avg": "",
                        "max": "",
                        "mdev": "",
                    },
                    "traceroute": "Gateway not implemented",
                }
            }
        )


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
        env["netbrain_pw"],
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
            target=worker,
            args=(nb, src, dst, env["device_user"], env["device_pw"], direction),
        )
        worker_threads.append(t)
        t.start()

    for t in worker_threads:
        t.join()

    results_queue.join()

    t1_stop = time.time()
    results.update({"exec_time": f"Took {t1_stop-t1_start :.3f} seconds to complete"})

    print(json.dumps(results))


if __name__ == "__main__":
    main()
