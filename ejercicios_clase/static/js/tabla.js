
var url = window.location.href

var tabla_url = url + '/tabla'

$.get(tabla_url, function(personas) {	

	var table_data = '';
	size = personas.length

	for(var i= 0; i < size; i++)
	{
		name = personas[i]['name'];
		//age = .....
		//nationality....

		table_data += '<tr>';

		table_data += '<td>'+name+'</td>';
		// Completar el resto de las columnas de datos de cada fila de la tabla
		// columna age....
		// columna nationality...

		table_data += '</tr>';

	}
	$("#list_table").append(table_data);
	

}); 

      
