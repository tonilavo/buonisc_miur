
$(document).ready(function(){
    //seleziona
    asilo_sel=$('#id_pr_asilo').val();

    tipo=$('#id_seltipoasilo').val();

    //mostro o nascondo i campi banca in base a risc diretta o no

    tipo_asilo=$('#id_seltipoasilo').val();

    carica_listaasili(tipo, asilo_sel);

     

    $("#id_seltipoasilo").change(function(){
        var tipo_asilo = $(this).val();
        x = carica_listaasili(tipo_asilo, 1);
        x = show_campi_allegati(tipo_asilo)
    });


    function carica_listaasili(tipo, asilo_selezionato) {
        dropdown = $('#id_selasilo');
        
        if ((location.hostname=='django-01.comune.grosseto.it') || (location.hostname=='django-04.comune.grosseto.it'))
            var Url_api= "/front/api/asili_json";
        else
            var Url_api= "http://www.comune.grosseto.it/buoniscuola-test/api/asili_json/";

        dropdown.empty();

        $.ajax({ 
            type: "GET",
            dataType: "json",
            url: Url_api,
            success: function(data){        
                if(data) {
                    x = 0;
                    data.results.forEach(element => {
                        if(element.tipo == tipo) {
                            if (element.id == asilo_selezionato)
                                dropdown.append("<option value='"+element.id+"' selected>"+element.nome+"</option>");
                            else
                                //dropdown.append($('<option></option>').attr('value', element.sc_codice).text(element.nome));
                                dropdown.append("<option value='"+element.id+"'>"+element.nome+"</option>");
                            x++;
                        }
                    });
                }
            }
         }); 
    }
    
});

   
   

    
