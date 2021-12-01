$('#analyze_path').click(() => {
    analyze_path();
});

function analyze_path() {
    source = $('#source').val();
    destination = $('#destination').val();

    $('#loading-progressbar').attr('style', 'display: block;');

    $.ajax({
        url: '/analyze/path',
        type: 'POST',
        data: `source=${source}&destination=${destination}`,
        dataType: 'text',
        success: function(response) {
            // Wrap all lines and replace empty lines with a <br>
            var modifiedResponse = [];
            response.split(/\r?\n/).forEach(function(val) {
                if (!val) {
                    modifiedResponse.push(`<br>`);
                } else {
                    modifiedResponse.push(`<div>${val}</div>`);
                }
            });

            // Wrap header
            // modifiedResponse[0] = `<div id="results-header">${modifiedResponse[0]}`;
            // modifiedResponse[1] = `${modifiedResponse[1]}</div>`;
            // modifiedResponse[2] = `<div id="results-body">${modifiedResponse[2]}`;
            // modifiedResponse[-1] = `${modifiedResponse[-1]}</div>`;

            $('#results').html(modifiedResponse);
            // $('#results').html(modifiedResponse.join(''));

            $('#results div').attr('style', 'font-family: "Roboto Mono", monospace;');
            $('#loading-progressbar').attr('style', 'display: none;');
        },
        error: function(xhr, status, error) {
            $('#loading-progressbar').attr('style', 'display: none;');
            window.alert('Something went seriously wrong');
        }
    });
}
