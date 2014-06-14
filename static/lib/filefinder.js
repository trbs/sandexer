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
        url: '/post',
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

function chart_browse_pie_filedistribution_spawn(target, data, source_name) {
    var c = $(target).highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: 0,
            plotShadow: false,
            margin: [0, 0, 0, 0],
            spacingTop: 0,
            spacingBottom: 0,
            spacingLeft: 0,
            spacingRight: 0,
            reflow: false
        },
        title: {
            text: 'File Distribution',
            align: 'center',
            verticalAlign: 'middle',
            y: -116
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                size: '100%',
                dataLabels: {
                    enabled: true,
                    distance: -40,
                    style: {
                        fontWeight: 'bold',
                        color: 'white',
                        textShadow: '0px 1px 2px black'
                    }
                },
                startAngle: -90,
                endAngle: 90,
                center: ['50%', '58%']
            }
        },
        credits: {
            enabled: false
        },
        series: [{
            type: 'pie',
            name: source_name,
            innerSize: '0%',
            data: data
        }]
    });
    return c;
}