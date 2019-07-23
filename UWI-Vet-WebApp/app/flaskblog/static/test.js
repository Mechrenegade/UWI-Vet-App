function get_student(){
    var id = $("#studentid").val()
    console.log(id);
    $.ajax({
        "headers": {
            "accept": "application/json",
        },
        url: '/student/'+id,
        method: 'GET', 
        success:(resp) => {
            
            // let text = $('<p>',{class:'test'}).append(resp)
            // $('#root').append(text)
            console.log(resp);
            $("#Name").html(resp.name)
            $("#ID").html(resp.id)
            $("#Date_enrolled").html(resp.date_enrolled)
            $("#Email").html(resp.email)
        }
    })
    $.ajax({
        "headers": {
            "accept": "application/json",
        },
        url: '/comp_rec/'+id,
        method: 'GET', 
        success:(resp) => {
            var output = " "
            var j = 0
            for(var i =0; i<resp["data"].length; i++){
                output+="<tr>";
                output+="<td>"+resp["data"][i].student_id+"</td>"
                //output+="<td>"+resp["data"][i].clinician_id+"</td>"
                output+="<td>"+resp["data"][i].comp_id+"</td>"
                //output+="<td>"+resp["data"][i].id+"</td>"
                if (resp["data"][i].mark==1){
                    output+=`<td><input type='checkbox' checked id='chkbx-${i}'></td>`;
                }
                else{
                    output+=`<td><input type='checkbox' id='chkbx-${i}'></td>`;
                }
                
                // output+="<td>"+resp["data"][i].mark+"</td>"
                
                output+="<td><button onclick='update("+resp["data"][i].id+","+i+")'>Update</button></td>"
                output+="</tr>"
            }
            
            $("#data").append(output)
            // let text = $('<p>',{class:'test'}).append(resp)
            // $('#root').append(text)
            console.log(resp);
        }
    })
}

function update(comp_id, chkbx_num){
    
    var x=$("#chkbx-"+chkbx_num).is(":checked");
    console.log(`#chkbx-${chkbx_num}`, x);
    $.ajax({
        "headers": {
            "accept": "application/json",
        },
        url: '/update_rec/'+comp_id+'/'+x,
        method: 'GET', 
        success:(resp) => {
            console.log(x); 
            console.log(resp);
        }
    })
    alert("Mark Updated!");
}

function get_exp(){
    var id = $("#studentid").val()
    console.log(id);
    $.ajax({
        "headers": {
            "accept": "application/json",
        },
        url: '/student/'+id,
        method: 'GET', 
        success:(resp) => {            
            // let text = $('<p>',{class:'test'}).append(resp)
            // $('#root').append(text)
            console.log(resp);
            $("#Name").html(resp.name)
            $("#ID").html(resp.id)
            $("#Date_enrolled").html(resp.date_enrolled)
            $("#Email").html(resp.email)
        }
    })
    $.ajax({
        "headers": {
            "accept": "application/json",
        },
        url: '/comp_rec/'+id,
        method: 'GET', 
        success:(resp) => {
            var output = " "
            for(var i =0; i<resp["data"].length; i++){
                output+="<tr>";
                output+="<td>"+resp["data"][i].student_id+"</td>"
                output+="<td>"+resp["data"][i].comp_id+"</td>"
                if (resp["data"][i].mark==1){
                    output+="<td>Signed</td>";
                }
                else{
                    output+="<td>Not Signed</td>";
                }
                output+="<td>"+resp["data"][i].clinician_id+"</td>"
                output+="</tr>"
            }
            $("#data").append(output)
            // let text = $('<p>',{class:'test'}).append(resp)
            // $('#root').append(text)
            console.log(resp);
        }
    })
}

function exportDoc(tableID, filename = ''){
    var downloadLink;
    var dataType = 'application/vnd.ms-excel';
    var tableSelect = document.getElementById(tableID);
    var tableHTML = tableSelect.outerHTML.replace(/ /g, '%20');
    
    // Specify file name
    filename = filename?filename+'.xls':'excel_data.xls';
    
    // Create download link element
    downloadLink = document.createElement("a");
    
    document.body.appendChild(downloadLink);
    
    if(navigator.msSaveOrOpenBlob){
        var blob = new Blob(['\ufeff', tableHTML], {
            type: dataType
        });
        navigator.msSaveOrOpenBlob( blob, filename);
    }else{
        // Create a link to the file
        downloadLink.href = 'data:' + dataType + ', ' + tableHTML;
    
        // Setting the file name
        downloadLink.download = filename;
        
        //triggering the function
        downloadLink.click();
    }
}