/**
 * Created with PyCharm.
 * User: dsc
 * Date: 5/30/14
 * Time: 11:01 AM
 */

$('#help').css('display', 'none');


function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

function post(data){
    $.ajax({
        type: 'POST',
        url: 'post',
        data: data,
        dataType: 'json',
        success: function(res){
            process(res)
        },
        error:function(zemmel){

        }
    });
}

function errorBox(errors){
    var text = '';
    for(var i = 0; i != errors.length ; i++){
        text += '<b>' + i + ':</b> ' + errors[i] + '<br>';
    }
    return '<div class=\"alert alert-danger\">'+text+'</div>';
}

function required_input(id){
    $('#'+id).fadeTo(300,0.3);
    setTimeout(function(){$('#'+id).fadeTo(200,1);}, 300);
}

$('#btn_help').click(function(){
    $('#help').css('display', 'block');
});


function check_form(show_errors){
    var warnings = [];
    var data = {};

    $('body *').each(function(){
        var $this = $(this);

        if($this.attr('data-req')){
            var id = $this.attr('id');
            var text = $this.html();

            if($this.attr('data-req') == 'yes' && text == 'Empty'){
                warnings.push('Property \'' + id + '\' cannot be empty.');
                required_input(id);
            }
            else{
                data[id] = text;
            }
        }
    });

    if(warnings.length == 0){
        return data;
    }
    else{
        if(show_alerts) $('#errorbox').html(errorBox(warnings));
    }
}