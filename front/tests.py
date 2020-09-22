from django.test import TestCase
from .tasks import *
from .models import *
from .domande_forms import *
from django.utils import timezone
import datetime

class DomandeTestCase(TestCase):

    id_domanda = 0
    id_ingresso = 0

    def setUp(self):
            cf_test = 'BRGLWG73S24I726A'
            test_token = tokens.generate(scope=(), key="", salt="None")
            rec_ingresso =Ingressi.objects.create(data_ingresso=datetime.datetime.now(), codfis_bimbo='BRGRLA16S69E202I',
                                            email="tonino.lavorati@gmail.com", codice_fiscale=cf_test,
                                            token=test_token, stato=0)

            rec_ingresso.save()
            self.id_ingresso = rec_ingresso.pk
            print("Creato ingresso num." + str(rec_ingresso.pk))

            domanda_data = {}
            domanda_data['pr_data_richiesta']=timezone.now()
            domanda_data['token'] = test_token
            domanda_data['so_cognome']='BARGAGLI'
            domanda_data['so_nome']='LUDWIG'
            domanda_data['so_nasc_dt'] = datetime.datetime(1973,11,24)
            domanda_data['so_nasc_com'] = 'SIENA'
            domanda_data['so_flag_residente']=1
            domanda_data['so_cod_fis'] = 'BRGLWG73S24I726A'
            domanda_data['so_sesso']='M'
            domanda_data['so_tel']='3284588472'
            domanda_data['so_email']='tonino.lavorati@gmail.com'
            domanda_data['pr_cognome']='BARGAGLI'
            domanda_data['pr_nome']='ARIEL'
            domanda_data['pr_sesso']='F'
            domanda_data['pr_nasc_dt']= datetime.datetime(2016,11,29)
            domanda_data['pr_nasc_com'] = 'GROSSETO'
            domanda_data['pr_codfiscale'] = 'BRGRLA16S69E202I'
            domanda_data['pr_fascia_asilo']='N'
            domanda_data['pr_tipo_asilo']='P'
            domanda_data['pr_spesa_mese']=180
            domanda_data['pr_spesa_totale']=1440
            domanda_data['pr_isee']= 5700
            domanda_data['pr_prot_isee_inps']='INPS-ISEE-2020-43567844-00'
            domanda_data['pr_data_isee_inps']=datetime.date(2020,4,22)
            domanda_data['so_risc_diretta']='N'
            domanda_data['so_banca_iban'] = 'IT76M0301503200000000218501'
            domanda_data['so_risc_diretta']='N'
            domanda_data['pr_spesa_mese'] = 280
            domanda_data['pr_num_tot_ricevute'] = 3
            domanda_data['pr_importo_tot_ricevute'] = 1400

            rec=Domande.objects.create(**domanda_data)

            print("creata domanda num."+str(rec.pk))
            self.id_domanda=rec.pk

    def test_annullamento_domanda(self):
        send_msg_domandanonvalida(self.id_domanda)
        print("test annullamento effettuato")

    def test_send_token(self):
        send_link_form(self.id_ingresso)
        print("test_send_token effettuato")

    def test_resend_token(self):
        resend_link_form(self.id_ingresso)
        print("test resend token effettuato")

    def testmsgfine(self):
        send_riep_domanda('tonino.lavorati@gmail.com', self.id_domanda)
        print("email di riepilogo domanda inviata")
