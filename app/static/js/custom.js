

function write_access_func() {
    var ip = $('#selectdev').select2('data')[0].text
    var port = $('#selected_port').val()
    var vlan = $('#selected_vlan').val()
    var send = {'write':JSON.stringify({'ip':ip, 'port':port, 'vlan':vlan})}
    $.ajax({
        url: '/access',
        type: 'POST',
        data: send,
        dataType: 'json',
        success: function(response) {
        $("#result").empty()
        $('#result').show()
        $("#result").append('<div id='+response+'><span class=" uk-text-lead uk-text-primary" id="taskdata"></span>&nbsp<span class="uk-text-lead" id="taskresult"></span></div>')
        if (JSON.stringify(response).includes('error')){
            UIkit.notification(JSON.stringify(response));
        }
        else {
            check_job_status(response)
            scroll("#result")
            }
        },
        error: function(error) {
            UIkit.notification('bok occurred')}
    })
}


function copyssh(){
    var filename = $('#filename').val()
    var username = $('#username').val()
    var password = $('#password')    .val()
    var sshpath = $('#sshpath').val()
    var send = {'copyssh': JSON.stringify([username,  password, filename, sshpath])}
    $.ajax({
        url: '/devtemplategen',
        type: 'POST',
        data: send,
        dataType: 'json',
        success: function(response) {
        $("#result").empty()
        $('#result').show()
        $("#result").append('<div id='+response+'><span class=" uk-text-lead uk-text-primary" id="taskdata"></span>&nbsp<span class="uk-text-lead" id="taskresult"></span></div>')
        if (JSON.stringify(response).includes('error')){
            UIkit.notification(JSON.stringify(response));
        }
        else {
            check_job_status(response)
            scroll("#result")
            }
        },
        error: function(error) {
            UIkit.notification('bok occurred')}
    })
}

function getvariables(){
    var template = $('.sel2 :selected').text()
    var send = {'getvaribles': template}
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: send,
        dataType: 'json',
        success: function(response) {
            $("#templatetable > tbody").html("");
            $("#render").show()
            console.log('template:'+template)
            $('#selected_tempate').val(template)
            console.log(response)
            $.each(response, function(i, j)
            {
                $('#templatetable').append('<tr><td><code>'+j.name+'</code></td><td>'+j.description+'</td><td><input value='+JSON.stringify(j.value)+' name='+j.name+' type="text"</td></tr>')

            })
                
        }
    })   
}


function editvariable(id, val) {
    selector =  $('#'+id).find('#'+val)
    var a = $.trim(selector.text())
    selector.replaceWith('<td id='+val+'_> <input  id='+val+' value="'+a+'" id='+id+' type="text"> <input   value="change" onclick="editvariable2(\''+id+'\',\''+val+'\')" class="uk-button uk-button-small uk-button-primary"></td>')
}

function editvariable2(id, val) {
    selector =  $('#'+id).find('#'+val)
    var send = {}
    send['name'] = id
    send[val] =  selector.val()
    var send = {'editvariable': JSON.stringify(send)}
    // console.log(send)
    
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: send,
        dataType: 'json',
        success: function(response) {
            // console.log(response)
            $('#'+id).find('#'+val+'_').replaceWith('<td  id="'+val+'">'+response+' <a><span onclick="editvariable(\''+id+'\',\''+val+'\')" class="uk-margin-small-right" uk-icon="icon:pencil"></span></a></td>')
            
        }
    })   
}



function checktrunk() {
    $('#checkbutton').replaceWith('<div id="checkbutton" uk-spinner></div>')
    var vlan = $('#vlan2').val()
    var cisco = $('#cisco').val()

    var send = {'check':JSON.stringify({'cisco':cisco, 'to_check':to_write, 'vlan':vlan})}
    $.ajax({
        url: '/checkmac',
        type: 'POST',
        data: send,
        dataType: 'json',

        success: function(response) {

        $(".resultlist2").empty()
        $(".resultlist2").append('<div id='+response+'><span class=" uk-text-lead uk-text-primary" id="taskdata"></span>&nbsp<span class="uk-text-lead" id="taskresult"></span></div>')
        if (JSON.stringify(response).includes('error')){
            UIkit.notification(JSON.stringify(response));
        }
        else {
            $("#resultlist2").empty()
            var cList = $('ul.resultlist2')
            $.each(response, function(i, j)
            {  
                var li = $('<li id='+j.job+'><span id="devtaskip"></span>&nbsp<span id="taskdata"></span>&nbsp<span id="taskresult"></span></li>')
                    .appendTo(cList);
                $('#'+j.job).find('#devtaskip').text(j.dev);    
                check_job_status(j.job)    
                    
            })
            }
        $('#checkbutton').replaceWith('<button id="checkbutton" class="uk-button uk-button-primary uk-button-large" onclick="checktrunk()">Check</button>')    
        },
        error: function(error) {
            $('#checkbutton').replaceWith('<button id="checkbutton" class="uk-button uk-button-primary uk-button-large" onclick="checktrunk()">Check</button>')            
            console.log(error);
            UIkit.notification('bok occurred')
        }          

    })
}




function write_func() {
    var send = {'vlan': $('#vlan').val(),'write_dict': JSON.stringify(to_write)}
    $( "#result" ).show();
    $.ajax({
        url: '/write',
        type: 'GET',
        data: send,
        dataType: 'json',   
        success:function(response) {
            if (JSON.stringify(response).includes('error')){
                UIkit.notification(JSON.stringify(response));
            }
            else {

            
            $("ul.resultlist").empty()
            var cList = $('ul.resultlist')
            $.each(response, function(i, j)
            {  
                var li = $('<li id='+j.job+'><span id="devtaskip"></span>&nbsp<span id="taskdata"></span>&nbsp<span id="taskresult"></span></li>')
                    .appendTo(cList);
                $('#'+j.job).find('#devtaskip').text(j.dev);    
                check_job_status(j.job)    
                    
            })
            scroll("#result") }
            $('#check').show()
            $('#vlan2').val($('#vlan').val())    
        }
    });
}

 
function deletestpdomain(domainid){
    UIkit.modal.confirm('Delete this domain?').then(function () {
        deletestpdomainconfirmed(domainid)
    }, function () {
        console.log('Rejected.')
    });

}
    





function deletestpdomainconfirmed(domainid){
    send = {'delete': domainid}
    $.ajax({
        url: '/stpdomains',
        type: 'GET',
        data: send,
        dataType: 'json',
        success: function(response) {
            console.log(response)
            $('#'+domainid).remove()
            UIkit.notification(response+' successfully deleted')

        }
    })
}






function editstpdomain(id){
    select =  []
    $('#'+id).find('.devlist').children('li').each(function(n,v){select.push($(this).text());})
    $('#'+id).find('.devlist').empty()
    $('#'+id).find('.devlist').append('<select id="'+id+'_field'+'" class="multipledevselect" multiple="multiple"></select>')
    sel2selector = id+'_field'
    domainid = id
    $('#'+id).find('.devlist').append('<button id="createstp" onclick="editstpdomain_send(\''+sel2selector+'\',\''+domainid+'\')" class="uk-button uk-button-primary">Edit</button>')
    multipledevselect()
    sel2 = $('#'+id).find('select')
    sel2.empty()
    $.each(select, function(i, j){
        sel2.append('<option value="id">'+j+'</option>').val('id').trigger('change');
    
    })
}



function editstpdomain_send(selector, domainid){
    var send = []
    var sel2data = $('#'+selector).select2('data')
    $.each(sel2data, function(i){
        send.push(sel2data[i].text)
    })
    send = {'edit':JSON.stringify([domainid,send]) }
    $.ajax({
        url: '/stpdomains',
        type: 'GET',
        data: send,
        success: function(response) {
            console.log(response)
            $('#'+domainid).find('.devlist').empty()
            var cList = $('#'+domainid).find('.devlist')
            $.each(response, function(i)
            {
                var li = $('<li/>')
                    .appendTo(cList)
                    .text(response[i]);

            })
            
        }
    })
}




function setport(a){
    $("#selected_port").val(a)
}



function getports(){
    var send = []
    $('#getports').replaceWith('<div id="getports" uk-spinner></div>')
    var sel2data = $('#selectdev').select2('data')[0].text
    send = {'emptyports':sel2data}
    $.ajax({
        url: '/access',
        type: 'POST',
        data: send,
        dataType: 'json',
        success: function(response) {
            $('#ports_table').empty()
            $('#ports_table').append('<th id="port">port</th><th id="admin">admin</th><th id="link">link</th>')
            ports = response
            $.each(ports, function(i)
            {
                $('#ports_table').append('<tr><td> <a href="#" onclick="setport('+ports[i][0]+'); return false;">'+ports[i][0]+'</a></td> <td>'+ports[i][1]["admin status"]+'</td><td>'+ports[i][1]["link status"]+'</td></tr>');  
            })
            $('#getports').replaceWith('<input type="button" class="scroll uk-button uk-button-primary" value="Get free ports" id="getports" onclick="getports()"/>')
            $('#stage1').show()
        },
        error: function(error) {
            $('#getports').replaceWith('<input type="button" class="scroll uk-button uk-button-primary" value="Get free ports" id="getports" onclick="getports()"/>')            
            console.log(error);
            UIkit.notification('bok occurred')
        }  
    
    });
}



function createstpdomain(){
    var send = []
    var sel2data = $('#createstp').select2('data')
    $.each(sel2data, function(i){
        send.push(sel2data[i].text)
    })
    send = {'create':JSON.stringify(send)}
    $.ajax({
        url: '/stpdomains',
        type: 'GET',
        data: send,
        dataType: 'json',
        success: function(response) {
            console.log(response)
            if (JSON.stringify(response).includes('error')){
                UIkit.notification(JSON.stringify(response));
            }
            else {
            $('#createstp').empty()
            domainid = Object.keys(response)[0]
            $('#ullist').append('<li id='+domainid+'>\
            <span>'+domainid+'</span> <span onclick="editstpdomain(\''+domainid+'\')" uk-icon="icon: pencil"></span><span onclick="deletestpdomain(\''+domainid+'\')" uk-icon="icon: trash"></span> \
            <ul class="devlist"><ul>\
            </li>')
            var cList = $('#'+domainid).find('.devlist')
            $.each(response[domainid], function(i)
            {
                var li = $('<li/>')
                    .appendTo(cList)
                    .text(response[domainid][i]);

            })
        }}
    })
}


function multipledevselect(){
$(".multipledevselect").select2({
    width: '400px',
    multiple: true,
    placeholder: "...",
    maximumSelectionSize: 12,
    minimumInputLength: 2,
    ajax: {
        url: '/dev_uri',
        delay: 250,
        processResults: function (data) {
            // Tranforms the top-level key of the response object from 'items' to 'results'
            return {results: data};
        },
        cache: true
    }
});
}





function check_job_status(taskid) {
    status_url = '/status/'+taskid
    $.getJSON(status_url, function(data) {
        console.log(data.status)
        switch (data.status) {
            case "started":
            case "queued":
                
                $('#'+taskid).find('#taskdata').text(data.status);
                setTimeout(function() {
                    check_job_status(taskid);
                }, 1000);
                         
            case "failed":
                $('#'+taskid).find('#taskdata').text(data.status);
                if (data.status != null){
                $('#'+taskid).find('#taskresult').text(data.result);}
                break;
                
            case "finished":    
                $('#'+taskid).find('#taskdata').text(data.status);
                if (data.status != null){
                    $('#'+taskid).find('#taskresult').text(data.result);}
                break;
                
            default:
                setTimeout(function() {
                check_job_status(taskid);
            }, 1000);
      }
    }
    );
}



function graph_update() {
    $.post('/systemupdate', function( data ) {
            $("#result").empty()
            // $("#result").append('<div id='+data+'><span id="taskdata"></span></div>')
            $("#result").append('<div id='+data+'><span class=" uk-text-lead uk-text-primary" id="taskdata"></span>&nbsp<span class="uk-text-lead" id="taskresult"></span></div>')
            $("#result").show()
            if (JSON.stringify(data).includes('errifor')){
                UIkit.notification(JSON.stringify(data));
            }
            else {check_job_status(data)}

        })
    $.post('system?status=True', function( data ) {
            $("#siteupdate").text(data[0])
            $("#graphupdate").text(data[1])
            })    
    };




function create() {
                $.ajax({
                    url: '/create',
                    type: 'GET',
                    success: function(response) {
                    var msg;
                    msg = "<i class='uk-icon-check'></i>" + response
                    $( "#stage1" ).show();
                    UIkit.notification(msg);
                        console.log(response);
                    scroll("#stage1")    
                    },
                    error: function(error) {
                        console.log(error);
                    }
                });
            };




function destroy() {
$.post('/exterminatus_work', function( data ) {
    console.log(data)
    $("#result").empty()
    $("#result").append('<div id='+data+'><span class=" uk-text-lead uk-text-primary" id="taskdata"></span>&nbsp<span class="uk-text-lead" id="taskresult"></span></div>')
    $("#result").show()
    if (JSON.stringify(data).includes('error')){
        UIkit.notification(JSON.stringify(data));
    }
    else {
    check_job_status(data)
    scroll("#result")
    }
})
};






function withports(){
    myArray2 = []
    res = $('.paths').find("input").toArray()
    $(res).each(function(i){
        if ($(res[i]).is(':checked')){
            myArray2.push(i)}})

    var send = {'items':JSON.stringify(myArray2), 'shortest': JSON.stringify(shortest)}
            $.ajax({
                    url: '/withports',
                    type: 'GET',
                    data: send,  
                    dataType: 'json',
                    success: function(response) {
                        $( "#stage4" ).show();
                        $("ul.preplist").empty()
                        var cList = $('ul.preplist')
                        var fancy = response[0];
                        to_write = response[1];
                        $.each(fancy, function(i)
                        {
                            var li = $('<li/>')
                                .appendTo(cList);
                            var aaa = $('<p class="uk-text-uppercase"/>')
                                .text(i+JSON.stringify(fancy[i]))
                                .appendTo(li);
                        })
                    scroll("#vlan")   
                    }
        });
};



function calc(){
    
    myArray =  [];
    var src;
    var dst;
    src = $('#src :selected').text();
    dst = $('#dst :selected').text();
    var send = {'src': $('#src :selected').text(),
                'dst': $('#dst :selected').text()}
    myArray.push(src, dst);
    $.ajax({
        url: '/shortest',
        type: 'GET',
        data: send,  
        dataType: 'json',
        success: function(response) {
            $( "#stage2" ).show()
            $( "#stage3" ).show()
            $("div.paths").empty()
            
            var cList = $('div.paths')
            shortest = response[1];
            var fancy = response[0];
            $.each(fancy, function(i)
            {
                var div = $('<div>')
                    .appendTo(cList);
                var checkbox = $('<input id=path'+i+' class="uk-checkbox" type="checkbox" checked><h2>Path '+i+'<h2>')
                    .appendTo(div);
                var ul = $('<ul class="uk-list uk-list-striped"/>')
                    .appendTo(div);
                $.each(fancy[i], function(j)
                {    var lili = $('<li/>')
                    .appendTo(ul)

                    var rext = $('<p class="uk-text-uppercase"/>')
                    .text(fancy[i][j])
                    .appendTo(lili);
                })    
            });
            scroll("#stage3")
        },
        error: function(error) {
            console.log(error);
            
        }
    });
    
};

function scroll(item){
    $('html, body').animate({
        scrollTop: $(item).offset().top
    }, 1000);
};