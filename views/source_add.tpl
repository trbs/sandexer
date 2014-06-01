<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sanderex - Admin</title>

    <!-- Bootstrap Core -->
    <link href="/static/lib/bootstrap-3.1.1-dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="/static/css/main.css" rel="stylesheet">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
    <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
    <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->

    <style>
        html,body{
            height: 100%
        }
        .form-control{
            border: 1px solid #A8A8A8;
        }
        .input-group-addon{
            border: 1px solid #A8A8A8;
            color: #8A8A8A;
            width: 80px;
        }
        input{
            width:256px;
        }
    </style>
</head>
<body>
<div class="blog-masthead">
    <div class="container">
        <nav class="blog-nav">
                <a class="blog-nav-item" href="/">Home</a>
                <a class="blog-nav-item" href="/search">Search</a>
                <a class="blog-nav-item" href="/info">Info</a>
                <a class="blog-nav-item" href="/logout">Logout</a>
                <a class="blog-nav-item active" href="/admin">Admin</a>
        </nav>
    </div>
</div>

<div class="container">
    <div style="height:20px;"></div>

    <ol class="breadcrumb">
        <li><a href="/admin">Admin</a></li>
        <li><a href="/admin/sources">Sources</a></li>
        <li class="active">Add a source</li>
    </ol>

    <div id="errorbox"></div>

    <h3>Source</h3>

    <table id="source" class="table table-bordered table-striped" style="clear: both">
        <tbody>
            <tr>
                <td width="35%">Name</td>
                <td width="65%"><a href="#" id="name" data-type="text" data-pk="1" data-req="yes" data-title="name"></a></td>
            </tr>
            <tr>
                <td width="35%">Protocol</td>
                <td width="65%"><a href="#" id="protocol" data-type="select" data-pk="1" data-req="yes" data-value="" data-title="Select protocol" class="editable editable-click" style=" background-color: rgba(0, 0, 0, 0);" data-original-title="" title=""></a></td>
            </tr>
            <tr>
                <td width="35%">Location</td>
                <td width="65%"><a href="#" id="url" data-type="text" data-req="yes" data-pk="1" data-title="Specifiy URL"></a></td>
            </tr>
        </tbody>
    </table>

    <h3>Crawler</h3>

    <table id="crawler" class="table table-bordered table-striped" style="clear: both">
        <tbody>
        <tr>
            <td width="35%">Interval (minutes)</td>
            <td width="65%"><a href="#" id="interval" data-type="text" data-req="yes" data-pk="1" data-title="Crawl Interval">10</a></td>
        </tr>
        <tr>
            <td width="35%">User-Agent</td>
            <td width="65%"><a href="#" id="useragent" data-type="text" data-req="yes" data-pk="1" data-title="User-Agent">Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0</a></td>
        </tr>
        </tbody>
    </table>

    <h3>Files</h3>

    <table id="filefilters" class="table table-bordered table-striped" style="clear: both">
        <tbody>
        <tr>
            <td width="35%">Include</td>
            <td width="65%"><a href="#" id="fileinclude_custom" data-req="yes" data-type="checklist" data-value="1,2,3,4,5" data-title="Select files" class="editable editable-click">Documents<br>Files<br>Movies<br>Music<br>Pictures</a></td>
        </tr>
        </tbody>
    </table>

    <a class="btn btn-large btn-default" href="/admin/sources">Cancel</a>
    <a id="submit_form" class="btn btn-large btn-default">Submit</a>
    <a id="btn_help" class="btn btn-large btn-default" style="float:right;">Help</a>
    <div style="height:50px;"></div>

    <div id="help">
        <div style="height:10px;"></div>

        <h4>Source Name</h4>
        The name will be visibile troughout the searches. It is a way of identifying this source from others.

        <div style="height:20px;"></div>

        <h4>Source Protocol</h4>
        Pick any of the available protocols.
        <div style="height:20px;"></div>

        <h4>Source Location</h4>
        The location to the source. Examples:
        <div style="margin-left:20px;margin-top:10px;">
        <b>HTTP(s) (url):</b><h4><span style="margin-left:20px;" class="label label-default">http://192.168.1.3/files/</span></h4>
        <br>
        <b>FTP (url):</b><h4><span style="margin-left:20px;" class="label label-default">ftp://192.168.1.3/files/</span></h4>
        </div>
        <div style="height:20px;"></div>

        <h4>Crawler Interval</h4>
        The time the crawler waits before visiting the source to discover new files, in minutes.
        <div style="height:20px;"></div>

        <h4>Crawler User-Agent</h4>
        The User-Agent of the crawler.
        <div style="height:20px;"></div>

        <h4>File Filters Include</h4>
        Specify what kind of files will be included in the listing.
        <div style="height:20px;"></div>
    </div>

    <div class="blog-footer">
    <p><a href="http://getbootstrap.com">Sanderex</a> v0.1 beta by <a href="https://github.com/skftn/">Sander 'dsc' Ferdinand</a>.</p>
    </div>

<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="/static/lib/bootstrap-3.1.1-dist/js/bootstrap.min.js"></script>

<!--<script src="static/lib/jquery-ui-1.10.4.custom/js/jquery-ui-1.10.4.custom.min.js"></script>-->
<!--<link href="static/lib/jquery-ui-1.10.4.custom/css/ui-darkness/jquery-ui-1.10.4.custom.min.css" rel="stylesheet">-->
<link rel="stylesheet" href="/static/lib/jquery-ui-1.10.4.custom/css/flick/jquery-ui-1.10.4.custom.min.css" />
<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/jquery-ui.min.js"></script>

<link href="/static/lib/jqueryui-editable/css/jqueryui-editable.css" rel="stylesheet">
<script src="/static/lib/jqueryui-editable/js/jqueryui-editable.js"></script>
<script src="/static/lib/filefinder.js"></script>

<script>
    $.fn.editable.defaults.mode = 'inline';
    $(document).ready(function(){
        $('#name, #url, #interval, #useragent').editable();
        $('#protocol').editable({
            source: [
                {value: 'HTTP', text: 'HTTP(s)'},
                {value: 'FTP', text: 'FTP'}
            ]

        });

        $('#fileinclude_custom').editable({
            pk: 1,
            limit: 5,
            source: [
                {value: 1, text: 'Documents'},
                {value: 2, text: 'Files'},
                {value: 3, text: 'Movies'},
                {value: 4, text: 'Music'},
                {value: 5, text: 'Pictures'}
            ]
        });

        $('#fileinclude').editable({
            source: [
                {value: 'ALL', text: 'Everything'},
                {value: 'CUSTOM', text: 'Custom'}
            ]

        });

        $('#submit_form').click(function(){
            check_form(false);
        });
    })
</script>
</body>
</html>