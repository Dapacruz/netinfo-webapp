<!DOCTYPE html>
<html lang="en">

<html>

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">

    <script type="application/javascript" src="static/js/jquery-3.4.1.min.js"></script>
    <script type="application/javascript" src="static/js/netinfo.js" defer></script>

    <title>NetInfo</title>
</head>

<body>
    <header>
    </header>
    <h1>NetInfo</h1>
    <div id="form">
        <input id="source" class="ui-input" type="text" placeholder="Source IP" value="10.248.7.2">
        <input id="destination" class="ui-input" type="text" placeholder="Destination IP" value="192.168.34.120">
        <button id="analyze_path" class="ui-button">Analyze Path</button>
        <div id="results">&nbsp;</div>
    </div>

    <div id="loading-progressbar" style="display: none;">
        <img src="static/img/ajax-loader.gif">
    </div>

</body>

</html>