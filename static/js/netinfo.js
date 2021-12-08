$('#analyze_path').click(() => {
    analyze_path();
});

$('#source, #destination').on('keyup', function (event) {
	if (event.keyCode == 13) {
		event.preventDefault();
		$('#analyze_path').click();
	}
});

var table;
var tableInitialized = false;

if (!tableInitialized) {
    tableInitialized = true;
    table = $('#netinfo').DataTable({
        columns: [
            { data: 'Source' },
            { data: 'Destination' },
            { data: 'Protocol' },
            { data: 'Latency' },
            { data: 'Type' },
            { data: 'Status' },
        ],

        paging: false,
        createdRow: (row, data, dataIndex, cells) => {
            if (data['Status'] == `open`) {
                $(cells[4]).addClass('openPort');
            } else {
                $(cells[4]).addClass('closePort');
            }
        }
    });
}

function analyze_path() {
    $('#errors').html('');
    $('#results').html('&nbsp;');
    source = $('#source').val();
    destination = $('#destination').val();

    if (!source || !destination) {
		console.log('You cannot leave the source or destination empty.');
		window.alert('You cannot leave the source or destination empty.');
		return;
    }

    $('.button').addClass('button--loading').prop("disabled",true);
   // $('#loading-progressbar').attr('style', 'display: block;');

    $.ajax({
        url: '/analyze/path',
        type: 'POST',
        timeout: 3*60*1000,
        data: `source=${source}&destination=${destination}`,
        dataType: 'json',
        success: function(response) {

            // Wrap all lines and replace empty lines with a <br>
            // var modifiedResponse = [];
            // response.split(/\r?\n/).forEach(function(val) {
            //     if (!val) {
            //         modifiedResponse.push(`<br>`);
            //     } else {
            //         modifiedResponse.push(`<div>${val}</div>`);
            //     }
            // });

            // Wrap headeriv id="results-body">${modifiedResponse[2]}`;
            // modifiedResponse[-1] = `${modifiedResponse[-1]}</div>`;

            // $('#results').html(response.reverse.ping_src);
            // netinfo.clear();
            // netinfo.rows.add(response.stdout.forward.ping_src).draw();
            // netinfo.rows.add(response.stdout.forward.ping_dst).draw();
            // netinfo.rows.add(response.stdout.reverse.ping_src).draw();
            // netinfo.rows.add(response.stdout.reverse.ping_dst).draw();
            if (response.stderr) {
                $('#errors').html(response.stderr);
            } else {
                html = `
                    <div>${JSON.stringify(response.stdout.forward.ping_src, null, 2)}</div>
                    <div>${JSON.stringify(response.stdout.forward.ping_dst, null, 2)}</div>
                    <div>${response.stdout.forward.traceroute.replace(/traceroute\s\n/, '')}</div>
                    <div>${JSON.stringify(response.stdout.reverse.ping_src, null, 2)}</div>
                    <div>${JSON.stringify(response.stdout.reverse.ping_dst, null, 2)}</div>
                    <div>${response.stdout.reverse.traceroute.replace(/traceroute\s\n/, '')}</div>
                    <div>${response.stdout.exec_time}</div>
                `
                $('#results').html(html);
            }

            // $('#results').html(JSON.stringify(response, null, 2));
            // $('#results').html(modifiedResponse.join(''));

            $('#results div').attr('style', 'font-family: "Roboto Mono", monospace;');
            $('.button').removeClass('button--loading').prop("disabled",false);
            //$('#loading-progressbar').attr('style', 'display: none;');
        },
        error: function(xhr, status, error) {
            console.log(xhr)
            console.log(status)
            console.log(error)
            $('.button').prop("disabled", false).removeClass('button--loading');
            //$('#loading-progressbar').attr('style', 'display: none;');
            window.alert('Something went seriously wrong');
        }
    });
}

