from rest_framework import serializers
from front.models import *
import pathlib

def get_attr_butt(butt_nome):
    attrib  = ' class="btn ' + butt_nome + ' btn-lg">'
    return  attrib

class IngressiSerializer(serializers.ModelSerializer):
    stato_parlato = serializers.SerializerMethodField()
    def get_stato_parlato(self, ingresso):
        if ingresso.stato==0:
            return "Da esaminare"
        elif ingresso.stato==2:
            return "Email inviata"
        elif ingresso.stato==5:
            return "Annullata con email"
        elif ingresso.stato==6:
            return "Annullata senza email"

    link_email = serializers.SerializerMethodField()
    def get_link_email(self, ingresso):
        if ingresso.stato == 0:
            url_dest = '<a href="/back/prep_email/?id=' + str(ingresso.id) + '"'
            butt_label = 'Email Continua'
            url_dest += get_attr_butt('btn-success') + butt_label  +'</a>'
            return url_dest
        elif ingresso.stato == 2:
            url_dest = '<a href="/back/resend_email/?id=' + str(ingresso.id) + '"'
            butt_label = 'Rimanda email'
            url_dest += get_attr_butt('btn-warning') + butt_label  +'</a>'
            return url_dest
        else:
            return ''

    link_domanda = serializers.SerializerMethodField()
    def get_link_domanda(self, ingresso):
        rec= Domande.objects.filter(token=ingresso.token)
        if rec.count() == 0 :
            if  ingresso.stato==2:
                return 'NO'
            else:
                return ''
        else:
            url_dest = '<a href="/back/reviewB_domanda/' + str(rec[0].id) + '">' + str(rec[0].id) + '</>'
            return url_dest

    class Meta:
        model = Ingressi
        fields = ['id', 'data_ingresso', 'codice_fiscale', 'codfis_bimbo','email', 'tel' ,'link_email','stato_parlato', 'link_domanda',]


class AllegatiSerializer(serializers.ModelSerializer):
   link_file = serializers.SerializerMethodField()
   def get_link_file(self, allegato):
       myfile= allegato.file
       if file_exists(myfile.path):
           ext= pathlib.Path(myfile.path).suffix
           if ext in ('.jpg', '.bmp', '.png', '.tif'):
               return '<img src="' + Allegati.objects.get(pk=allegato.pk).file.url + '" class="img-thumbnail" alt="File"> '
           else:
            return '<a href="' + Allegati.objects.get(pk=allegato.pk).file.url + '" target="_blank">File</a>'
       else:
           return '----------'

   class Meta:
        model = Allegati
        fields =  ['id', 'domanda_num', 'descrizione', 'file', 'link_file']

def file_exists(file_path):
    try:
        with open(file_path):
            return True
            # Do something with the file
    except IOError:
        return False


class DomandeSerializer(serializers.ModelSerializer):

    ut_tel = serializers.SerializerMethodField()
    def get_ut_tel(self, domanda):
        ingressi = Ingressi.objects.filter(codice_fiscale=domanda.so_cod_fis)
        if ingressi.count()>0:
            ingresso=ingressi[0]
        else:
            return ""
        if ingresso.tel != None:
            return ingresso.tel
        else:
            return ""
    stato_parlato = serializers.SerializerMethodField()
    def get_stato_parlato(self, domanda):
        if domanda.pr_stato==0:
            return "Aperta"
        elif domanda.pr_stato==1:
            return "Da esaminare"
        elif domanda.pr_stato==2:
            return "Confermata da uff."
        elif domanda.pr_stato==5:
            return "Annullata da uff."

    link_edit = serializers.SerializerMethodField()
    def get_link_edit(self, domanda):
            url_dest = '<a href="/back/reviewB_domanda/'+str(domanda.id)+'" '
            butt_label = 'Dettaglio'
            url_dest += get_attr_butt('btn-light') + butt_label  +'</a>'
            print(url_dest)
            return url_dest

    link_del = serializers.SerializerMethodField()
    def get_link_del(self, domanda):
        textmsg="Confermi la cancellazione della domanda n." + str(domanda.id) + '?'
        url_dest = '<a href="/back/del_domanda/' + str(domanda.id) +  '" onclick="return confirm(\'' + textmsg + '\')"'
        butt_label = 'Cestina'

        if domanda.pr_stato  < 2:
            url_dest += get_attr_butt('btn-danger') + butt_label  +'</a>'
            return url_dest
        else:
            url_dest += ' class="btn btn-danger disabled btn-lg" >' + butt_label  +'</a>'
            return url_dest

    link_riapri = serializers.SerializerMethodField()
    def get_link_riapri(self, domanda):
        textmsg="Confermi la riapertura della domanda n." + str(domanda.id) + '?'
        url_dest = '<a href="/back/riapri_domanda/' + str(domanda.id) +  '" onclick="return confirm(\'' + textmsg + '\')"'
        butt_label = 'Riapri'

        if domanda.pr_stato >= 1 :  #si mette sempre abilitato
            url_dest += get_attr_butt('btn-warning') + butt_label  +'</a>'
            return url_dest
        else:
            url_dest += ' class="btn  btn-danger disabled  btn-lg">' + butt_label  +'</a>'
            return url_dest

    link_rifiuta = serializers.SerializerMethodField()
    def get_link_rifiuta(self, domanda):
        function_js='"getConfirmation('+  str(domanda.id) + ');"'
        textmsg = "Confermi l'annullamento della domanda n." +  str(domanda.id) + '?'
        url_dest = '<a href="/back/send_domandanonvalida/' + str(domanda.id) +  '" onclick="return confirm(\'' + textmsg + '\')"'
        butt_label = 'Comunica dati errati'

        if domanda.pr_stato == 1:
            url_dest += get_attr_butt('btn-danger') + butt_label  +'</a>'
            return url_dest
        else:
            url_dest += ' class="btn  btn-danger disabled  btn-lg">' + butt_label  +'</a>'
            return url_dest

    link_conferma = serializers.SerializerMethodField()
    def get_link_conferma(self, domanda):
        textmsg="Confermi la domanda n." + str(domanda.id) + '?'
        url_dest = '<a href="/back/conferma_domanda/'+str(domanda.id) +  '" onclick="return confirm(\'' + textmsg + '\')"'
        butt_label = 'Conferma dati'
        if domanda.pr_stato <= 1:
            url_dest += get_attr_butt('btn-success') + butt_label  +'</a>'
            return url_dest
        else:
            url_dest += ' class="btn btn-success disabled btn-lg" >' + butt_label  +'</a>'
            return url_dest

    class Meta:
        model = Domande
        fields = ['id', 'pr_data_richiesta', 'so_cod_fis', 'ut_tel', 'pr_isee', 'so_email', 'pr_cognome', 'pr_nome', 'pr_codfiscale',   'pr_fascia_asilo', 'pr_tipo_asilo', 'stato_parlato', 'link_edit', 'link_conferma', 'link_del', 'link_riapri', 'link_rifiuta']
