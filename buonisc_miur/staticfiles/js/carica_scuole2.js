
$(document).ready(function(){
    
    fascia=$('#id_selfasciascuola').val();

    carica_listascuole(fascia);

    document.getElementById('id_so_email').readOnly = true;
    document.getElementById('id_so_cod_fis').readOnly = true;

    $("#id_selfasciascuola").change(function(){
        var tiposc = $(this).val();
        x = carica_listascuole(tiposc);
    });

    function carica_listascuole(fascia) {
        dropdown = $('#id_selscuola');
        var Url_api= "/api/scuole_json";

        dropdown.empty();

        $.ajax({ 
            type: "GET",
            dataType: "json",
            url: Url_api,
            success: function(data){        
                if(data) {
                    x = 0;
                    data.results.forEach(element => {
                        if(element.tipo === fascia) {
                            dropdown.append($('<option></option>').attr('value', element.sc_codice).text(element.nome));
                            x++;
                        }
                    });
                }
            }
         }); 
    }

    $("#id_so_risc_diretta").change(function(){
            var selected = $(this).val();

            if (selected == 'S') {
                document.getElementById("riga_banca").style.display = "none";     
            
            } else {
                document.getElementById("riga_banca").style.display = "block";     
            }       
    });
    
});

   
   

    
