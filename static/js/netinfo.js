let analyze_path_btn = document.querySelector('#analyze_path');
document.querySelectorAll('.ui-input').forEach((e) => {
    e.addEventListener('keyup', function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            analyze_path_btn.click();
        }
    });
});

let table;
let tableInitialized = false;
if (!tableInitialized) {
    tableInitialized = true;
    table = $('#netinfo').DataTable({
        columns: [
            { data: 'Gateway' },
            { data: 'Source' },
            { data: 'Destination' },
            { data: 'Latency' },
            { data: 'Protocol' },
            { data: 'Type' },
            { data: 'Status' },
        ],

        paging: false,
        // createdRow: (row, data, dataIndex, cells) => {
        //     if (data['Status'] == `open`) {
        //         $(cells[4]).addClass('openPort');
        //     } else {
        //         $(cells[4]).addClass('closePort');
        //     }
        // }
    });
}

analyze_path_btn.addEventListener('click', analyze_path);

function sleep(s) {
    return new Promise(resolve => setTimeout(resolve, s * 1000));
}

async function analyze_path() {
    const button = document.querySelector('.button');
    const errors = document.querySelector('#errors');
    const results = document.querySelector('#results');
    const source = document.querySelector('#source').value;
    const destination = document.querySelector('#destination').value;

    table.clear();
    table.draw();

    errors.style.fontFamily = '"Roboto Mono", monospace';
    errors.innerHTML = '&nbsp;';

    results.style.fontFamily = '"Roboto Mono", monospace';
    results.innerHTML = '&nbsp;';

    if (!source || !destination) {
        console.log('You cannot leave the source or destination empty.');
        window.alert('You cannot leave the source or destination empty.');
        return;
    }

    // Change button color to indicate that the analysis is running
    button.classList.add('button--loading');
    button.setAttribute("disabled", true);
    button.innerHTML = 'Analyzing Path ...';
    button.style.backgroundColor = '#3d3d3d';
    button.style.cursor = 'not-allowed';

    let response = await fetch(`/analyze/path?source=${source}&destination=${destination}`);

    if (response.ok) {
        let data = await response.json();
        const job_id = data.jobid;
        console.log(`Job ID: ${job_id}`);

        do {
            await sleep(10);
            response = await fetch(`/get/results?job_id=${job_id}`);
            // console.log(response.status)
            if (response.status === 200) {
                data = await response.json();
                console.log(data);
            }
        }
        while (response.status === 204);

        if (data.stderr) {
            errors.innerHTML = data.stderr;
        } else {
            // html = `
            //     <div>${JSON.stringify(data.stdout.forward.ping_src, null, 2)}</div>
            //     <div>${JSON.stringify(data.stdout.forward.ping_dst, null, 2)}</div>
            //     <div>${data.stdout.forward.traceroute.replace(/traceroute\s\n/, '')}</div>
            //     <div>${JSON.stringify(data.stdout.reverse.ping_src, null, 2)}</div>
            //     <div>${JSON.stringify(data.stdout.reverse.ping_dst, null, 2)}</div>
            //     <div>${data.stdout.reverse.traceroute.replace(/traceroute\s\n/, '')}</div>
            //     <div>${data.stdout.exec_time}</div>
            // `
            // html = `
            // <div>${data.stdout.forward.traceroute.replace(/traceroute\s\n/, '')}</div>
            // <div>${data.stdout.reverse.traceroute.replace(/traceroute\s\n/, '')}</div>
            // <div>${data.stdout.exec_time}</div>
            // `
            html = `
                <div>${data.stdout.forward.traceroute}</div>
                <div>${data.stdout.reverse.traceroute}</div>
                <div>${data.stdout.exec_time}</div>
            `;
            results.innerHTML = html;

            // Add string good/bad to table status
            table.row.add({
                Gateway: data.stdout.reverse.ping_src.gateway,
                Source: data.stdout.reverse.ping_src.source,
                Destination: data.stdout.reverse.ping_src.destination,
                Latency: data.stdout.reverse.ping_src.avg+' ms',
                Protocol: '',
                Type: 'Ping',
                Status: ''
            });
            table.row.add({
                Gateway: data.stdout.reverse.ping_dst.gateway,
                Source: data.stdout.reverse.ping_dst.source,
                Destination: data.stdout.reverse.ping_dst.destination,
                Latency: data.stdout.reverse.ping_dst.avg+' ms',
                Protocol: '',
                Type: 'Ping',
                Status: ''
            });
            table.row.add({
                Gateway: data.stdout.forward.ping_src.gateway,
                Source: data.stdout.forward.ping_src.source,
                Destination: data.stdout.forward.ping_src.destination,
                Latency: data.stdout.forward.ping_src.avg+' ms',
                Protocol: '',
                Type: 'Ping',
                Status: ''
            });
            table.row.add({
                Gateway: data.stdout.forward.ping_dst.gateway,
                Source: data.stdout.forward.ping_dst.source,
                Destination: data.stdout.forward.ping_dst.destination,
                Latency: data.stdout.forward.ping_dst.avg+' ms',
                Protocol: '',
                Type: 'Ping',
                Status: ''
            });
            table.draw();
        }

        button.classList.remove('button--loading');
        button.removeAttribute("disabled");
        button.innerHTML = 'Analyze Path';
        button.style.backgroundColor = '#0b7dda';
        button.style.cursor = 'pointer';
    } else {
        button.classList.remove('button--loading');
        button.removeAttribute("disabled");
        button.innerHTML = 'Analyze Path';
        button.style.backgroundColor = '#0b7dda';
        button.style.cursor = 'pointer';
        window.alert('Something went seriously wrong');
    }
}
