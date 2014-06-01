<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FileFinder - Search</title>

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
    </style>
</head>
<body>
<div class="blog-masthead">
    <div class="container">
        <nav class="blog-nav">
                <a class="blog-nav-item active" href="/">Home</a>
                <a class="blog-nav-item" href="/search">Search</a>
                <a class="blog-nav-item" href="/info">Info</a>
                <a class="blog-nav-item" href="/logout">Logout</a>
                %if view.is_admin == True:
                    <a class="blog-nav-item" href="/admin">Admin</a>
                %end
        </nav>
    </div>
</div>

<div class="container">
    <div style="height:20px;"></div>

    %if view.important_message:
        <h3>Important Message</h3>
        {{view.important_message}}
    %end

    <div class="blog-footer" style="position: fixed;">
        <p><a href="http://getbootstrap.com">Sanderex</a> v0.1 beta by <a href="https://github.com/skftn/">Sander 'dsc' Ferdinand</a>.</p>
    </div>

<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="static/lib/bootstrap-3.1.1-dist/js/bootstrap.min.js"></script>
</body>
</html>