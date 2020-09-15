
$(document).ready(function(){
    //seleziona asili
    asilo_sel=$('#id_pr_asilo').val();

    tipo=$('#id_seltipoasilo').val();

    //mostro o nascondo i campi banca in base a risc diretta o no
    risc_diretta=$('#id_so_risc_diretta').val();
    x=show_campi_banca(risc_diretta);
    tipo_asilo=$('#id_seltipoasilo').val();
    show_campi_allegati(tipo_asilo);
    carica_listaasili(tipo, asilo_sel);
    hide_domicilio($('#id_so_flag_residente').val());

    $("#id_seltipoasilo").change(function(){
        var tipo_asilo = $(this).val();
        x = carica_listaasili(tipo_asilo, 1);
        x = show_campi_allegati(tipo_asilo)
    });

    $("#id_so_flag_residente").change(function(){
        var residenteSN = $(this).val();
        x = hide_domicilio(residenteSN);
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

    function show_campi_banca(risc_diretta) {
        if (risc_diretta == 'S') {
            document.getElementById("id_iban").style.display = "none";

        } else {
            document.getElementById("id_iban").style.display = "block";
        }
    }

    function show_campi_allegati(tipo_asilo) {
        if (tipo_asilo == 'C') {
            document.getElementById("riga_ricevute").style.display = "none";

        } else {
            document.getElementById("riga_ricevute").style.display = "block";
        }
    }

    function hide_domicilio(residenteSN) {
        target = document.getElementById("domicilio");
        if (residenteSN == 1) { // residente
            target.style.display = "none";
            target.val='';

        } else { // non residente
            target.style.display = "block";
        }
    }

    $("#id_so_risc_diretta").change(function(){
            var risc_diretta = $(this).val();
            x=show_campi_banca(risc_diretta);
    });

});
