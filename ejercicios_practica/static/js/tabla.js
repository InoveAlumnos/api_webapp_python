
var url = window.location.href

var tabla_url = url + '/tabla'

$.get(tabla_url, function(personas) {	

	var table_data = '';
	size = personas.length

	for(var i= 0; i < size; i++)
	{
		name = personas[i]['name'];
		age = personas[i]['age'];
		nationality = personas[i]['nationality'];

		table_data += '<tr>';

		table_data += '<td>'+name+'</td>';
		table_data += '<td>'+age+'</td>';
		table_data += '<td>'+nationality+'</td>';

		table_data += '</tr>';

	}
	$("#list_table").append(table_data);
	

}); 

      
