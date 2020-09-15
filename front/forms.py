from django import forms
from django.forms import ModelForm
from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field, Fieldset, HTML
from crispy_forms.bootstrap import TabHolder, Tab, AppendedText, PrependedText, StrictButton
#from codicefiscale import isvalid as isvalid_cf
from codicefiscale import codicefiscale
from .models import *
from django.utils import timezone
from django.conf import settings
import re, datetime

class Preform(ModelForm):

    class Meta:
        model = Ingressi
        fields = ('codice_fiscale', 'codfis_bimbo',  'email', 'protocollo_inps', 'isee', 'data_dsu', 'tel' )
        labels = {'codice_fiscale':'cod.fiscale', 'codfis_bimbo': 'cod.fiscale del minore', 'email': 'email', 'tel': 'telefono', 'isee':'valore Isee', 'protocollo_inps':'num.protocollo', 'data_dsu': 'data presentazione DSU'}
        widget = {'data_dsu': DatePickerInput(format='%d/%m/%Y', options={'locale': 'it'})}

    def clean(self):
        data =self.cleaned_data
        print("inizio clean")

        #controllo codice fiscale bimbo
        codfiscale = data.get('codfis_bimbo').upper()

        if not codicefiscale.is_valid(codfiscale):
            raise forms.ValidationError('Codice fiscale del minore non corretto')
        #ricerca di predomande per questo bimbo
        recs=Ingressi.objects.filter(codfis_bimbo=codfiscale, stato__lte=2)
        if recs.count() > 0 and not self.instance.pk: #esiste un'altra preform con lo stesso cidfis minore e stato non annullato
            raise forms.ValidationError('Richiesta per il bimbo con cod.fiscale '+ codfiscale + ' già presente.')
        data['codfis_bimbo'] = codfiscale

        #controllo codice fiscale richiedente
        codfiscale = data.get('codice_fiscale').upper()
        if not codicefiscale.is_valid(codfiscale):
            raise forms.ValidationError('Codice fiscale del richiedente non corretto')

        data['codice_fiscale'] = codfiscale

        #controllo protocollo INPS
        currdata = timezone.now()
        curranno =  currdata.strftime("%Y")

        protdsu=data.get('protocollo_inps').upper()
        prefix = 'INPS-ISEE-'
        prima_parte_curranno  =  prefix + curranno  + '-'
        prima_parte_annoprec  =  prefix + str(int(curranno)-1)  + '-'

        if ((protdsu[0:15] != prima_parte_curranno)  and (protdsu[0:15] != prima_parte_annoprec))  or  (protdsu[24:27] != '-00')  or (protdsu == prefix + curranno  +'-XXXXXXXXX-00'):
            #or (protdsu == 'INPS-ISEE-' +  curranno + '-XXXXXXXXX-00')
            raise forms.ValidationError('Inserire un numero protocollo DSU nel formato INPS-ISEE-anno-XXXXXXXXX-00 con anno '+ str(int(curranno)-1) + ' oppure ' + curranno)
        data['protocollo_inps'] = protdsu

        if data.get('data_dsu') < datetime.date(int(curranno)-1, 1, 1):
            raise forms.ValidationError("Ammesse solo date dal I gennaio " + str(int(curranno)-1))
        elif data.get('data_dsu') > datetime.date.today():
            raise forms.ValidationError("Ammesse solo date passate")
        #controllo limite Isee
        isee_max = 30000
        if (data.get('isee') > isee_max):
            raise forms.ValidationError('Il valore massimo Isee ammesso per la richiesta contributo è di '+ str(isee_max))

        data['email'] = data.get('email').upper()
        self.cleaned_data = data
        #print(" ---  VALIDAZIONE TERMINATA    ----")
        #print(self.cleaned_data)
        if self.errors:
            print("Errori")
            print(self.errors)

        return self.cleaned_data


class CrispyPreForm(Preform):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('codfis_bimbo', css_class='form-control  col-md-6 mb-6'),
                css_class='form-row ', style='padding-bottom:70px;'
            ),
            Fieldset("Dati del richiedente",
            Div(
                Row(
                Column('email', css_class='form-control col-md-6 mb-6', style='padding-right:50px;'),
                css_class='form-row ', style='padding-bottom:70px;'
                ),
                Row(
                Column('codice_fiscale', css_class='form-control  col-md-6 mb-6'),
                Column('tel', css_class='form-control col-md-4 mb-6'),
                css_class='form-row ', style='padding-bottom:70px;'
                )),
                Fieldset('Dati della DSU',
                Row(
                Column('isee', css_class='form-control col-md-6 mb-6', style='padding-right:50px;'),

                Column('data_dsu', css_class='form-control  col-md-4 mb-4'),
                css_class='form-row  ', style='padding-bottom:70px;'
                ),
                Row(
                Column('protocollo_inps', css_class='form-control col-md-6 mb-4'),
                css_class='form-row  ', style='padding-bottom:70px;'
                )
            ),
            Row(
                HTML('<div class="g-recaptcha" data-sitekey="6LdTmPUUAAAAAJHs1p_cn9ME_qOOw5264feotBNr" style="padding-bottom:30px;padding-right:40px;"></div>'),
                Column(Submit('submit', 'Salva'), css_class='form-control col-md-6 mb-6'),
                css_class='form-row', style='padding-bottom:20px;'
            )
        ))

class PreformNoCaptcha(ModelForm):

    class Meta:
        model = Ingressi
        fields = ('codice_fiscale', 'email', 'protocollo_inps', 'isee', 'data_dsu' )
        labels = {'codice_fiscale':'codice fiscale', 'protocollo_inps':'num.protocollo DSU', 'data_dsu': 'Data DSU'}
        widget = {'data_dsu': forms.DateInput(attrs={'class':'datepicker'})}

    def clean(self):
        data =self.cleaned_data

        #controllo codice fiscale
        codfiscale = data.get('codice_fiscale').upper()
        if not isvalid_cf(codfiscale):
            raise forms.ValidationError('Codice fiscale non corretto')

        data['codice_fiscale'] = codfiscale
        #controllo protocollo INPS
        currdata = timezone.now()
        curranno =  currdata.strftime("%Y")

        protdsu=data.get('protocollo_inps').upper()

        if (protdsu[0:15] != 'INPS-ISEE-'+ curranno  +'-')  or (protdsu[24:27] != '-00') or (protdsu == 'INPS-ISEE-' + curranno  +'-XXXXXXXXX-00'):
            #or (protdsu == 'INPS-ISEE-' +  curranno + '-XXXXXXXXX-00')
            raise forms.ValidationError('Inserire un numero protocollo DSU nel formato INPS-ISEE-2020-XXXXXXXXX-00')
        data['protocollo_inps'] = protdsu

        if data.get('data_dsu') < datetime.date(int(curranno), 1, 1):
            raise forms.ValidationError("Ammesse solo date dell'anno corrente")
        elif data.get('data_dsu') > datetime.date.today():
            raise forms.ValidationError("Ammesse solo date passate")
        if (data.get('isee') > 15748.78):
            raise forms.ValidationError('Il valore massimo Isee ammesso per la richiesta contributo è di 15748,78')

        data['email'] = data.get('email').upper()

        return self.cleaned_data
