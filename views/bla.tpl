<!DOCTYPE html>
<html>
<head>
    <title>
        Tutorialsavvy.com : Bottle framework template demo
    </title>
    <style>
        .searchkeyword{
            color:blue;
        }
        .fruit{
            color:green;
        }
        .flower{
            color:orange;
        }
        .else-style{
            color:grey;
        }
    </style>
</head>
<body>

<h3>Your Favourite <span class='searchkeyword'>{{item}}</span> are :</h3>

%if  'fruit'== item:
<ul class="fruit">
    <li>Orange</li>
    <li>Apple</li>
    <li>Mango</li>
    <li>Water Melon</li>
    <li>Grapes</li>
</ul>
%elif 'flower' == item:
<ul class="flower">
    <li>Rose</li>
    <li>Jasmine</li>
    <li>Lotus</li>
    <li>Tulip</li>
    <li>Lily</li>
</ul>
%else :
<h3 class="else-style">No Fruit or Flower catagory is Selected</h3>

</body>
</html>