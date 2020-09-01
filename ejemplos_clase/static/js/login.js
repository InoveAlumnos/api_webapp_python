$(document).ready(function(){
    $('.btn-send').click(function(e)
    {
        e.preventDefault();

        name = document.getElementById('nombre').value;
        var url = window.location.href

        $.post(url, {name: name},
            function(data) {
                document.location.href=data
            }
        );
 
    });
});