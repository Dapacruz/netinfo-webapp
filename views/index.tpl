<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta http-equiv="X-UA-Compatible" content="ie=edge" />
    <link rel="stylesheet" type="text/css" href="static/css/Lato.css">
    <link rel="stylesheet" type="text/css" href="static/css/Roboto-Mono.css">
    <link rel="stylesheet" type="text/css" href="static/css/jquery-ui-1.12.1.twilight/jquery-ui.css" />
    <link rel="stylesheet" type="text/css" href="static/js/DataTables/DataTables-1.10.20/css/dataTables.jqueryui.css" />
    <link rel="stylesheet" type="text/css"
        href="static/js/DataTables/FixedHeader-3.1.6/css/fixedHeader.dataTables.css" />
    <link rel="stylesheet" type="text/css" href="static/js/DataTables/Select-1.3.1/css/select.jqueryui.css" />
    <link rel="stylesheet" type="text/css" href="static/css/styles.css" />
    <link rel="stylesheet" type="text/css" href="static/css/loading.css" />
    <link rel="stylesheet" type="text/css" href="static/css/loading.min.css" />
    <link rel="icon" type="image/png" href="/static/img/favicon1.png">
    <script src="static/js/jquery-3.4.1.min.js" defer></script>
    <script type="text/javascript" src="static/js/DataTables/DataTables-1.10.20/js/jquery.dataTables.js" defer></script>
    <script type="text/javascript" src="static/js/DataTables/DataTables-1.10.20/js/dataTables.jqueryui.js" defer></script>
    <script type="text/javascript" src="static/js/DataTables/FixedHeader-3.1.6/js/dataTables.fixedHeader.js" defer></script>
    <script type="text/javascript" src="static/js/DataTables/Select-1.3.1/js/dataTables.select.js" defer></script>
    <script type="text/javascript" src="static/js/DataTables/Buttons-1.6.1/js/dataTables.buttons.js" defer></script>
    <script type="text/javascript" src="static/js/DataTables/Buttons-1.6.1/js/buttons.html5.js" defer></script>
    <script type="text/javascript" src="static/js/DataTables/Buttons-1.6.1/js/buttons.colVis.js" defer></script>
    <script type="application/javascript" src="static/js/netinfo.js" defer></script>
</head>
<body>
    <a href="/"><img border="0" src="/static/img/logo.png" alt="Logo" width="450" height="100"></a>
    <div id="form">
        <input id="source" class="ui-input" type="text" placeholder="Source IP"><br>
        <input id="destination" class="ui-input" type="text" placeholder="Destination IP"><br>
        <button id="analyze_path" class="button"><span class="button__text">Analyze Path</span></button>
    </div>
    <pre id="errors" style="color:red;">&nbsp;</pre>
    <div>
        <table id="netinfo" class="display">
            <thead>
                <th>Gateway</th>
                <th>Source</th>
                <th>Destination</th>
                <th>Latency</th>
                <th>Protocol</th>
                <th>Type</th>
                <th>Status</th>
            </thead>
            <tbody>
            </tbody>
        </table>
    </div>
    <pre id="results">&nbsp;</pre>
    <div id='loading-message'>
        <img src='static/img/ajax-loader.gif' />
    </div>
</body>
</html>