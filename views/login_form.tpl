<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FileFinder - Login Required!</title>

    <!-- Bootstrap Core -->
    <link href="static/lib/bootstrap-3.1.1-dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="static/css/main.css" rel="stylesheet">

    <!-- Even more custom styles for this template -->
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
            %if login:
                <meta http-equiv="refresh" content="0;URL='/loggedin'" />
            %else:
<a class="blog-nav-item active" href="login">Login</a>
            %end
        </nav>
    </div>
</div>

<div class="container">
    %if ascii:
    <pre style=font-size:8px;font-weight:bold;font-family:monospace;border:0px;>
                                       ..
                                     .(  )`-._
                                   .'  ||     `._
                                 .'    ||        `.
                              .'       ||          `._
                            .'        _||_            `-.
                         .'          |====|              `..
                       .'             \__/               (  )
                     ( )               ||          _      ||
                     /|\               ||       .-` \     ||
                   .' | '              ||   _.-'    |     ||
                  /   |\ \             || .'   `.__.'     ||   _.-..
                .'   /| `.            _.-'   _.-'       _.-.`-'`._`.`
                \  .' |  |        .-.`    `./      _.-`.    `._.-'
                 |.   |  `.   _.-'   `.   .'     .'  `._.`---`
                .'    |   |  :   `._..-'.'        `._..'  ||
               /      |   \  `-._.'    ||                 ||
              |     .'|`.  |           ||_.--.-._         ||
              '    /  |  \ \       __.--'\    `. :        ||
               \  .'  |   \|   ..-'   \   `._-._.'        ||
`.._            |/    |    `.  \  \    `._.-              ||
    `-.._       /     |      \  `-.'_.--'                 ||
         `-.._.'      |      |        | |         _ _ _  _'_ _ _ _ _
              `-.._   |      \        | |        |_|_|_'|_|_|_|_|_|_|
                  [`--^-..._.'        | |       /....../|  __   __  |
                   \`---.._|`--.._    | |      /....../ | |__| |__| |
                    \__  _ `-.._| `-._|_|_ _ _/_ _ _ /  | |__| |__| |
                     \   _o_   _`-._|_|_|_|_|_|_|_|_/   '-----------/
                      \_`.|.'  _  - .--.--.--.--.--.`--------------'
      .```-._ ``-.._   \__   _    _ '--'--'--'--'--'  - _ - _  __/
 .`-.```-._ ``-..__``.- `.      _     -  _  _  _ -    _-   _  __/(.``-._
 _.-` ``--..  ..    _.-` ``--..  .. .._ _. __ __ _ __ ..--.._ / .( _..``
`.-._  `._  `- `-._  .`-.```-._ ``-..__``.-  -._--.__---._--..-._`...```
   _.-` ``--..  ..  `.-._  `._  `- `-._ .-_. ._.- -._ --.._`` _.-`LGB`-.
    </pre>
    %end

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
        <div class="blog-footer" style="position: fixed;">
            <p><a href="http://getbootstrap.com">FileFinder</a> v0.1 beta by <a href="https://github.com/skftn/">Sander 'dsc' Ferdinand</a>.</p>
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