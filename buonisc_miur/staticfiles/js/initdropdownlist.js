
$(document).ready(function() {

    load_json_data('id_pr_fascia_scuola');

    function load_json_data(id, tipo) {
        var html_code = '';
        $.getJSON('scuole.json', 
            function(data) {
                //html_code += '<option value="">Select ' + tipo + '</option>';
                $.each(data, function(key, value) {
                if (id == 'id_pr_scuola') {
                    if (value.tipo == tipo) {
                        html_code += '<option value="' + value.id + '">' + value.nome + '</option>';
                    }
                }   
                }
            });

            $('#' + id).html(html_code);
        });
        }

        $(document).on('change', '#id_pr_fascia_scuola', function() {
            var tiposc = $(this).val();
            if (tiposc != '') {
                load_json_data('tipo', tiposc);
            } 
            else {
                $('#id_pr_scuola').html('<option value="">Select scuola</option>');
            }

        });

});