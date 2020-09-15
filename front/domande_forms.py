from .models import *
from django import forms
from crispy_forms.helper import FormHelper
from django.forms import ModelForm, Select, Textarea, HiddenInput
from crispy_forms.bootstrap import InlineRadios
from crispy_forms.layout import *
#from codicefiscale import isvalid as isvalid_cf, build as build_cf
from codicefiscale import codicefiscale
import re, datetime
from django.conf import settings
from datetime import date
from django.utils import timezone
from localflavor.generic.models import IBANField
from localflavor.generic.countries.sepa import IBAN_SEPA_COUNTRIES
import os


class MyModel(models.Model):
    iban = IBANField(include_countries=IBAN_SEPA_COUNTRIES)


SEX_CHOICES = (
    ('M', 'M'),
    ('F', 'F'),
    ('', '')
)

RISC_CHOICES = (
    ('S', 'Per cassa'),
    ('N', 'Tramite banca')
)
SN_CHOICES = (
    (1, 'Si'),
    (0, 'No'),
)
FASCIAASILO_CHOICES = (
    (None, '----'),
    ('N', 'Nido'),
    ('M', 'Materna'),
)

TIPOASILO_CHOICES = (
    (None, '----'),
    ('C', 'Comunale'),
    ('P', 'Di privati'),
)

ASILO_CHOICES = (
    (None, '----'),
)


class Domandeform(ModelForm):

    class Meta:
        model = Domande
        fields = '__all__'

        labels = {'pr_data_richiesta': 'Data inserimento', 'so_cognome': 'Cognome', 'so_nome': 'Nome',
                  'so_sesso': 'Sesso', 'so_nasc_dt': 'Data di nascita',
                  'so_nasc_com': 'Comune di nascita', 'so_cod_fis': 'Cod.fiscale ', 'so_banca_iban': 'IBAN',
                  'pr_prot_isee_inps': 'num.protocollo DSU', 'pr_isee': 'Isee', 'so_email': 'Email',
                  'so_domicilio': 'Domicilio', 'so_flag_residente': 'Residente nel Comune di Grosseto',
                  'so_risc_diretta': 'Modalità di riscossione', 'pr_cognome': 'Cognome', 'pr_nome': 'Nome',
                  'pr_sesso': 'Sesso', 'pr_codfiscale': 'cod.fiscale', 'pr_fascia_asilo': 'Fascia asilo',
                  'pr_tipo_asilo': 'Comunale/Privato', 'pr_nasc_dt': 'data nascita', 'pr_nasc_com': 'Comune nascita',
                  'pr_spesa_mese': 'Spesa mensile', 'pr_imp_buoniscuola': 'Imp.riscosso Buoni scuola',
                  'pr_imp_buoniinps': 'Imp.riscosso Buoni Inps', 'pr_spesa_totale': 'Spesa totale',
                  'pr_num_tot_ricevute': 'Numero', 'pr_importo_tot_ricevute': 'Importo totale'
                  }

        widgets = {'so_risc_diretta': Select(choices=RISC_CHOICES), 'pr_tipo_asilo': forms.HiddenInput,
                   'pr_asilo': forms.HiddenInput,
                   'so_sesso': Select(choices=SEX_CHOICES), 'pr_sesso': Select(choices=SEX_CHOICES),
                   'pr_prot_isee_inps': forms.HiddenInput,
                   'pr_nasc_dt': forms.SelectDateWidget(years=[date.today().year - i - 3 for i in range(5)]),
                   'pr_data_isee_inps': forms.HiddenInput, 'token': forms.HiddenInput, 'pr_stato': forms.HiddenInput,
                   'so_flag_residente': Select(choices=SN_CHOICES),

                   }


class CrispyDomandaForm(Domandeform):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        testo_init = '<div class="panel-heading pagetitlehome titolopagina" style="padding-left: 30px;padding-top:60px;padding-bottom:30px;">'
        testo_init += "<p><b>Riempire tutti i campi sottostanti per l'assegnazione di buoni scuola per scuole dell'infanzia</b>\
                            </p>I campi con asterisco sono obbligatori</div>"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(testo_init),
            Row(
                Column('pr_data_richiesta', css_class='form-control disabled col-md-4 mb-2',
                       style='padding-right:20px;'),
                css_class='form-row col-12', style='padding-bottom:40px;padding-left:20px;'
            ),
            Fieldset("Richiedente",
                     Row(
                     Column('so_cod_fis', css_class='form-control disabled col-md-4 mb-2', style='padding-right:20px;'),
                     Column('pr_isee', css_class='form-control   col-md-2 mb-6', style='background-color: gray10;'),
                     Column('so_email', css_class='read-only form-control col-sm-4 mb-6'),
                     css_class='form-row col-12', style='padding-bottom:40px;padding-left:20px;'
                     ),
                    Row(
                        Column('so_cognome', css_class='form-control col-md-4 mb-2', style='padding-right:50px;'),
                        Column('so_nome', css_class='form-control col-md-4 mb-2', style='padding-right:50px;'),
                        Column('so_sesso', css_class='form-control col-md-2 mb-2'),
                        css_class='form-row col-6', style='padding-bottom:60px'
                    ),
                    Row(
                        Column('so_nasc_dt', css_class='form-control col-md-4 mb-2', style='padding-right:70px;'),
                        Column('so_nasc_com', css_class='form-control col-md-4 mb-2'),
                        css_class='form-row col-6', style='padding-bottom:100px'
                    ),
                    Row(
                        Column('so_flag_residente', css_class='form-control col-md-2 mb-6'),
                        Div(
                            Field('so_domicilio'),
                            css_id='domicilio'),
                        css_class='form-row col-6', style='padding-bottom:130px'
                    )
            ),
            Fieldset('Dati  anagrafici del  minore',
                 Row(
                     Column('pr_codfiscale', css_class='form-control col-md-4 mb-2', style='padding-right:30px;'),
                     Column('pr_cognome', css_class='form-control col-md-4 mb-2', style='padding-right:30px;'),
                     Column('pr_nome', css_class='form-control col-md-4 mb-2', style='padding-right:30px;'),
                     css_class='form-row col-6', style='padding-bottom:60px'
                 ),
                 Row(
                     Column('pr_nasc_dt', css_class='form-control col-md-4 mb-2'),
                     Column('pr_nasc_com', css_class='form-control col-md-4 mb-2'),
                     Column('pr_sesso', css_class='form-control col-md-2 mb-2'),
                     css_class='form-row  col-6', style='padding-bottom:100px;'
                 )
                 ),
            Fieldset('Dati di frequenza',
                 Row(
                     Column('pr_fascia_asilo', css_class='form-control col-md-4 mb-4'),
                     Column('pr_tipo_asilo', css_class='form-control col-md-4 mb-4'),
                     Column('pr_spesa_mese', css_class='form-control col-md-4 mb-2', style='padding-left:30px;'),
                     Column('pr_spesa_totale', css_class='form-control col-md-2 mb-4'),
                     Column('pr_imp_buoniscuola', css_class='form-control col-md-2 mb-4'),
                     Column('pr_imp_buoniinps', css_class='form-control col-md-2 mb-4'),
                     css_class='form-row  col-6', style='padding-top:10px;padding-bottom:15px;'
                 ),
                 ),
                Div(
                    Fieldset('Ricevute allegate',
                     Row(
                         Column('pr_num_tot_ricevute', css_class='form-control col-sm-2 mb-2',
                                style='padding-right:30px;'),
                         Column('pr_importo_tot_ricevute', css_class='form-control col-sm-4 mb-4'),
                         css_class='form-row  col-sm-6', style='padding-bottom:75px;'
                     ),
                     ), css_id="riga_ricevute"
            ),
            Fieldset('Dati per la riscossione',
                 Row(
                     Column('so_risc_diretta', css_class='form-control col-md-0 mb-2'),
                     css_class='form-row  col-8', style='padding-bottom:30px;'
                 ),
                 Row(
                     Column('so_banca_iban', css_class='col-md-4', css_id="id_iban"),
                     css_class='form-row  col-8', style='padding-bottom:30px; '
                 )
            ),
            Row(
                HTML(
                    '<div class="g-recaptcha" data-sitekey="6LdTmPUUAAAAAJHs1p_cn9ME_qOOw5264feotBNr" style="padding-bottom:60px;padding-right:40px;"></div>'),
                Column(Submit('submit', 'Salva'), css_class='form-control col-md-6 mb-6'),
                css_class='form-row', style='padding-top:60px;padding-bottom:30px;'
            ),
            Row(Column(
                Field('pr_tipo_asilo'),
                Field('pr_asilo'),
                Field('pr_prot_isee_inps'),
                Field('pr_data_isee_inps'),
                Field('token')
            ),
        ))

    def clean(self):

        data = self.cleaned_data
        # controllo codice fiscale  richiedente
        if data.get('so_cod_fis'):
            codice_fiscale = data.get('so_cod_fis').upper()
            if not codicefiscale.is_valid(codice_fiscale):
                raise forms.ValidationError('Codice fiscale del richiedente non corretto')

            dt_nascita=data.get('so_nasc_dt')
            str_dtnascita = str(dt_nascita.day) + '/' + str(dt_nascita.month) + '/' + str(dt_nascita.year)

            dati_decodecf =  codicefiscale.decode(codice_fiscale)
            if dati_decodecf['birthplace']['name'] != data.get('so_nasc_com').upper():
                raise forms.ValidationError('Luogo di nascita non coerente con quello ricavato dal codice fiscale del richiedente.')

            #cf_calcolato= build_cf(data.get('pr_cognome'), data.get('pr_nome'), datetime.datetime(dt_nascita.year, dt_nascita.month, dt_nascita.day),  data.get('pr_sesso'), comune_cf)
            cf_calcolato = codicefiscale.encode(surname=data.get('so_cognome'), name=data.get('so_nome'), sex=data.get('so_sesso'), birthdate=str_dtnascita, birthplace=data.get('so_nasc_com'))
            if (cf_calcolato != codice_fiscale) and (codice_fiscale not in codicefiscale.decode(cf_calcolato)['omocodes']):
                alert_msg = 'Codice fiscale del richiedente non coerente con i dati anagrafici indicati'
                raise forms.ValidationError(alert_msg)
            data['so_cod_fis'] = codice_fiscale

        if data.get('pr_codfiscale'):
            codice_fiscale = data.get('pr_codfiscale').upper()
            if not codicefiscale.is_valid(codice_fiscale):
                raise forms.ValidationError('Codice fiscale del minore non corretto')

            dt_nascita=data.get('pr_nasc_dt')
            str_dtnascita = str(dt_nascita.day) + '/' + str(dt_nascita.month) + '/' + str(dt_nascita.year)

            dati_decodecf =  codicefiscale.decode(codice_fiscale)
            if dati_decodecf['birthplace']['name'] != data.get('pr_nasc_com').upper():
                raise forms.ValidationError('Luogo di nascita non coerente con quello ricavato dal codice fiscale del minore.')

            #cf_calcolato= build_cf(data.get('pr_cognome'), data.get('pr_nome'), datetime.datetime(dt_nascita.year, dt_nascita.month, dt_nascita.day),  data.get('pr_sesso'), comune_cf)
            cf_calcolato = codicefiscale.encode(surname=data.get('pr_cognome'), name=data.get('pr_nome'), sex=data.get('pr_sesso'), birthdate=str_dtnascita, birthplace=data.get('pr_nasc_com'))
            #print("CF calcolato:"+cf_calcolato)
            if (cf_calcolato != codice_fiscale) and (codice_fiscale not in codicefiscale.decode(cf_calcolato)['omocodes']):
                raise forms.ValidationError('Codice fiscale del minore non coerente con i dati anagrafici')

            # controllo presenza domanda con stesso codice fiscale alunno
            domande_alunno = Domande.objects.filter(pr_codfiscale=codice_fiscale, pr_stato__gte=0, pr_stato__lt=5)
            if domande_alunno.count() > 1:
                if not self.instance.pk:  # siamo in inserimento
                    raise forms.ValidationError(
                        'Già presente in archivio una richiesta di buoni scuola per minore con cod.fiscale:' + codice_fiscale)
                elif self.instance.pk != domande_alunno[0].id:  # in fase di modifica
                    raise forms.ValidationError(
                        'Già presente in archivio una richiesta di buoni scuola per minore con cod.fiscale:' + codice_fiscale)

        # controllo valid. data di nascita
        if data.get('pr_nasc_dt'):
            if data.get('pr_nasc_dt') < datetime.date(2013, 1, 1):
                raise forms.ValidationError("Anno di nascita minimo 2013")
            elif data.get('pr_nasc_dt') >= date.today():
                raise forms.ValidationError("Ammesse solo date passate per data nascita")

        # controllo presenza tutti i campi IBAN per riscossione banca
        if data.get('so_risc_diretta') == 'N':
            if not data.get('so_banca_iban'):
                raise forms.ValidationError("Indicare l'IBAN dell'intestatario")
        # controlli sui dati frequenza
        if not data.get('pr_mesi_frequenza') or data.get('pr_mesi_frequenza') == 0 or data.get(
                'pr_mesi_frequenza') > 12:
            raise forms.ValidationError(
                "Indicare il numero di mesi di frequenza della scuola dell'infanzia (valore da 1 a 12)")

        if data.get('seltipoasilo') == 'P':
            if not data.get('pr_num_tot_ricevute'):
                raise forms.ValidationError(
                    "Indicare il numero delle ricevute da allegare per la frequenza della scuola dell'infanzia privata")
            if not data.get('pr_importo_tot_ricevute'):
                raise forms.ValidationError(
                    "Indicare la somma totale delle ricevute da allegare per la frequenza della scuola dell'infanzia privata")
        # controlli sui dati domicilio per non residenti
        print("controllo dati residenza:" + str(data.get('so_flag_residente')))
        if data.get('so_flag_residente') == 0:
            if not (data.get('so_domicilio')):
                raise forms.ValidationError("Obbligatorio, per in non residenti, indicare il domicilio")

        if not data.get('pr_data_richiesta'):
            data['pr_data_richiesta'] = timezone.now

        data['so_cognome'] = data.get('so_cognome').upper()
        data['so_nome'] = data.get('so_nome').upper()
        data['so_nasc_com'] = data.get('so_nasc_com').upper()
        data['pr_cognome'] = data.get('pr_cognome').upper()
        data['pr_nome'] = data.get('pr_nome').upper()
        data['pr_nasc_com'] = data.get('pr_nasc_com').upper()
        data['so_flag_residente'] = data.get('so_flag_residente')
        data['pr_stato'] = 0

        return data


class PhotoForm(forms.Form):
    descrizione = forms.CharField(label="Descrizione dell'allegato (es. ricevuta dicembre)", max_length=65,
                                  required=False)
    file = forms.FileField(required=False)

    def clean_file(self):
        my_file = self.cleaned_data.get("file", None)

        if not self.cleaned_data.get("file"):
            raise forms.ValidationError('Selezionare il file da caricare')

        destination = settings.MEDIA_ROOT
        if os.path.isfile(destination + my_file.name):
            raise forms.ValidationError(
                'Esiste già un file di nome "' + my_file.name + '". Per favore rinomina il file')

        return my_file

    def clean(self):
        data = self.cleaned_data
        if not data.get("descrizione"):
            raise forms.ValidationError("Inserire una descrizione dell'allegato che stiamo caricando")
        return data


class TestJsform(forms.Form):
    seltipoasilo = forms.CharField(max_length=1, label="Tipo di scuola dell'infanzia",
                                   widget=Select(choices=TIPOASILO_CHOICES), initial='')
    selasilo = forms.CharField(max_length=100, label='Denominazione', widget=Select(choices=ASILO_CHOICES))


class CrispyTestJsform(TestJsform):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        testo_init = '<div class="panel-heading pagetitlehome titolopagina" style="padding-left: 30px;padding-top:60px;padding-bottom:30px;">'
        testo_init += "<p><b>Riempire tutti i campi sottostanti per l'assegnazione di buoni scuola per scuole dell'infanzia</b>\
                            </p>I campi con asterisco sono obbligatori</div>"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(testo_init),
            Fieldset("Scuola d'infanzia",
                     Row(
                         Column('seltipoasilo', css_class='form-control   col-md-2 mb-6'),
                         Column('selasilo', css_class='form-control disabled col-sm-4 mb-2',
                                style='padding-right:60px;'),
                     ),
                     ))
