<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sanderex - Login Required!</title>

    <!-- Bootstrap Core -->
    <link href="static/lib/bootstrap-3.1.1-dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="static/css/main.css" rel="stylesheet">

    <!-- Even more custom styles for this template -->
    <style>
        html,body{
            height: 100%;
        }
        .form-control{
            border: 1px solid #A8A8A8;
        }
        .input-group-addon{
            border: 1px solid #A8A8A8;
            color: #8A8A8A;
            width: 80px;
        }
        div.bg_container{
            margin-top:0;
            margin-bottom:0;
            height: 100%;
            width: 100%;
            position:fixed;
            top:48px;
            background-color: #bcd3e6;
        }
        div.bg_lower_container{
            position: fixed;
            width:100%;
            height:478px;
            bottom:0;
        }
        div.bg_repeat{
            background-image: url('/static/images/login_bg_repeat.png');
            background-position: right center;
            height: 478px;
            width: auto;
            overflow: hidden;
        }
        div.bg_leftcorner{
            background-image: url('/static/images/login_bg_leftcorner.png');
            width:792px;
            height: 478px;
            bottom:0;
            right:0;
            float:right;
        }
    </style>
</head>
<body>

<div class="blog-masthead">
    <div class="container">
        <nav class="blog-nav">
            %if login:
                <meta http-equiv="refresh" content="0;URL='/loggedin'" />
            %else:
                <a class="blog-nav-item active" href="login">Login</a>
            %end
        </nav>
    </div>
</div>

<div class="bg_container">
    <div class="bg_lower_container">
        <div class="bg_leftcorner">

        </div>
        <div class="bg_repeat">

        </div>

    </div>
</div>

<div class="container">
    <div class="row">

        <div class="col-sm-8 blog-main">
            <div style="height:{{'20' if ascii else '40'}}px;width:100%"></div>

            <form action="login_post" method="post" name="login">
            <div class="input-group input-group-sm">
                <span class="input-group-addon">Username</span>
                <input name="username" id="box_username" type="text" class="form-control" placeholder="" style="width:210px;">
            </div>

            <div style="height:10px;"></div>

            <div class="input-group input-group-sm">
                <span class="input-group-addon">Password</span>
                <input name="password" id="box_password" type="password" class="form-control" placeholder="" style="width:210px;">
            </div>

            <div style="height:10px;"></div>

            <div style="width:290px;">
                <button id="login" type="submit" class="btn btn-default btn-sm" style="float:right;">Login</button>
                <div id="warning" style="font-size:11px;padding-top:6px;padding-left:90px;color:red;">

                </div>
            </div>
            </form>

        </div>
    </div>

<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="static/lib/filefinder.js"></script>
<script src="static/lib/bootstrap-3.1.1-dist/js/bootstrap.min.js"></script>

<script>
    $(document).ready(function(){
        var ref = document.referrer;
        if(endsWith(ref, '/login')){
            $('#warning').text('Login not valid.');
            $('#warning').fadeOut(2500);
        }
    });
</script>
</body>
</html>