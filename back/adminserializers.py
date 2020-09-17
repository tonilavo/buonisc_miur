from rest_framework import serializers
from front.models import *
import pathlib
from django.conf import settings

def get_url_prefix():
	if settings.USE_ABSOLUTE_PATH == 'True':
		if settings.HOSTNAME[0:7] != "http://":
			hostname = "http://" + settings.HOSTNAME
		else:
			hostname = settings.HOSTNAME

		return hostname
	else:
		return '/front'

def get_attr_butt(butt_nome):
    attrib  = ' class="btn ' + butt_nome + ' btn-lg">'
    return  attrib


class AdminDomandeSerializer(serializers.ModelSerializer):

    link_edit = serializers.SerializerMethodField()
    def get_link_edit(self, domanda):
            url_dest = '<a href="/back/reviewB_domanda/'+str(domanda.id)+'" '
            butt_label = 'Dettaglio'
            url_dest += get_attr_butt('btn-light') + butt_label  +'</a>'
            print(url_dest)
            return url_dest

    link_riapri = serializers.SerializerMethodField()
    def get_link_riapri(self, domanda):
        function_js='"getConfirmation('+  str(domanda.id) + ');"'
        url_dest = '<a href="/back/riapri_domanda/' + str(domanda.id) + '"  onclick=' + function_js
        butt_label = 'Riapri'

        if domanda.pr_stato == 1:
            url_dest += get_attr_butt('btn-danger') + butt_label  +'</a>'
            return url_dest
        else:
            url_dest += ' class="btn  btn-danger disabled  btn-lg">' + butt_label  +'</a>'
            return url_dest

    link_user = serializers.SerializerMethodField()
    def get_link_user(self, domanda):
        url_dest = '<a href="'+ get_url_prefix() +'/domanda/?token=' + domanda.token +  '" '
        butt_label = 'Conferma dati'
        url_dest += get_attr_butt('btn-success') + butt_label  +'</a>'
        return url_dest


    class Meta:
        model = Domande
        fields = ['id', 'pr_data_richiesta', 'so_cod_fis',  'so_email', 'pr_cognome', 'pr_nome', 'pr_codfiscale', 'pr_tipo_asilo', 'pr_stato', 'link_edit', 'link_user', 'link_riapri']
