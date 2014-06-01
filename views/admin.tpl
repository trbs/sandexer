<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sanderex - Admin</title>

    <!-- Bootstrap Core -->
    <link href="static/lib/bootstrap-3.1.1-dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="static/css/main.css" rel="stylesheet">

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
                %if view.is_admin == True:
                    <a class="blog-nav-item active" href="/admin">Admin</a>
                %end
        </nav>
    </div>
</div>

<div class="container">
    <div style="height:20px;"></div>

    <div id="errorbox"></div>

    <div class="list-group">
        <a href="#" class="list-group-item">
            <h4 class="list-group-item-heading">General</h4>
            <p class="list-group-item-text">Turns dials, rotate knobs and such.</p>
        </a>
        <a href="/admin/sources" class="list-group-item">
            <h4 class="list-group-item-heading">Sources</h4>
            <p class="list-group-item-text">Add a remote source.</p>
        </a>
        <a href="/admin/access" class="list-group-item">
            <h4 class="list-group-item-heading">Access control</h4>
            <p class="list-group-item-text">Add, remove and ban users.</p>
        </a>
        <a href="/admin/debug" class="list-group-item">
            <h4 class="list-group-item-heading">Debug</h4>
            <p class="list-group-item-text">Debug shit.</p>
        </a>
    </div>

    <div class="blog-footer">
    <p><a href="http://getbootstrap.com">Sanderex</a> v0.1 beta by <a href="https://github.com/skftn/">Sander 'dsc' Ferdinand</a>.</p>
    </div>

<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="static/lib/bootstrap-3.1.1-dist/js/bootstrap.min.js"></script>

<!--<script src="static/lib/jquery-ui-1.10.4.custom/js/jquery-ui-1.10.4.custom.min.js"></script>-->
<!--<link href="static/lib/jquery-ui-1.10.4.custom/css/ui-darkness/jquery-ui-1.10.4.custom.min.css" rel="stylesheet">-->
<link rel="stylesheet" href="static/lib/jquery-ui-1.10.4.custom/css/flick//jquery-ui-1.10.4.custom.min.css" />
<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/jquery-ui.min.js"></script>

<link href="static/lib/jqueryui-editable/css/jqueryui-editable.css" rel="stylesheet">
<script src="static/lib/jqueryui-editable/js/jqueryui-editable.js"></script>
<script src="static/lib/filefinder.js"></script>

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