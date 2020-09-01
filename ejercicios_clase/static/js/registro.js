$(document).ready(function(){
    $('.btn-send').click(function(e)
    {
        e.preventDefault();

        name = document.getElementById('nombre').value;
        age = document.getElementById('edad').value;
        nationality = document.getElementById('nacionalidad').value;

        var url = window.location.href

        $.post(url, {name: name, age: age, nationality: nationality},
            function(data) {
                    
            }
        );
 
    });
});