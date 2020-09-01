$(document).ready(function(){
    $('.btn-send').click(function(e)
    {
        e.preventDefault();

        heart_rate = document.getElementById('pulsos').value;

        var url = window.location.href

        $.post(url, {heartrate: heart_rate},
            function(data) {
                $('#div_image').html('<img src="data:image/png;base64,' + data + '" />');      
                    
            }
        );
 
    });
});