
var url = window.location.href

// Agregado para evitar que un onclick arruine las url
if(url.slice(-1) == '#')
{
	url = url.substring(0, url.length - 1);
}

function view(name) {
	
	var historico_url = url + '/' + name + '/historico'
	
	window.location = historico_url
}

var tabla_url = url + '/tabla'

$.get(tabla_url, function(personas) {	

	var table_data = '';
	size = personas.length

	for(var i= 0; i < size; i++)
	{
		name = personas[i]['name'];
		last_record_time = personas[i]['time'];
		last_record_value = personas[i]['last_heartrate'];
		record_count = personas[i]['records'];

		table_data += '<tr>';
		table_data += '<td>'+name+'</td>';
		table_data += '<td>'+last_record_time+'</td>';
		table_data += '<td>'+last_record_value+'</td>';
		table_data += '<td>'+record_count+'</td>';
		//table_data += '<td><a href="#" class="btn-view" onclick="view(\'' + name + '\')">Ver</a></td>';
		table_data += '<td><a href="#" class="btn-view" onclick="view(\'' + name + '\')"><span style="font-size: 3em; color: Tomato;"><i class="fas fa-search"></i></span></a></td>';
		table_data += '</tr>';

	}
	$("#list_table").append(table_data);
	

}); 

      
