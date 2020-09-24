from django import forms
from django.forms import ModelForm
from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field, Fieldset, HTML
from crispy_forms.bootstrap import TabHolder, Tab, AppendedText, PrependedText, StrictButton
from codicefiscale import codicefiscale
from .models import *
from django.utils import timezone
from django.conf import settings
import re, datetime

class Preform(ModelForm):

    class Meta:
        model = Ingressi
        fields = ('codice_fiscale', 'codfis_bimbo',  'email', 'tel' )
        labels = {'codice_fiscale':'cod.fiscale del richiedente', 'codfis_bimbo': 'cod.fiscale del minore', 'email': 'email'}

    def clean(self):
        data =self.cleaned_data
        #controllo codice fiscale bimbo
        codfiscale = data.get('codfis_bimbo').upper()

        if not codicefiscale.is_valid(codfiscale):
            raise forms.ValidationError('Codice fiscale del minore non corretto')
        #ricerca di predomande per questo bimbo
        recs=Ingressi.objects.filter(codfis_bimbo=codfiscale, stato__lte=2)
        if recs.count() > 0 : #esiste un'altra preform con lo stesso cidfis minore e stato non annullato
        #and not self.instance.pk
            raise forms.ValidationError('Richiesta  già presente per il minore con cod.fiscale '+ codfiscale + '.')

        data['codfis_bimbo'] = codfiscale

        #controllo codice fiscale richiedente
        codfiscale = data.get('codice_fiscale').upper()
        if not codicefiscale.is_valid(codfiscale):
            raise forms.ValidationError('Codice fiscale del richiedente non corretto')

        data['codice_fiscale'] = codfiscale.upper()
        data['email'] = data.get('email').upper()

        self.cleaned_data = data
        if self.errors:
            print(self.errors)

        return self.cleaned_data

class CrispyPreForm(Preform):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('codice_fiscale', css_class='form-control  col-md-6 mb-6'),
                css_class='form-row  col-md-8', style='padding-bottom:90px;'
                ),
            Row(
                Column('email', css_class='form-control col-md-6 mb-6', style='padding-right:50px;'),
                Column('tel', css_class='form-control col-md-6 mb-6'),
                css_class='form-row col-md-12', style='padding-bottom:90px;'
                ),
            Row(
                Column('codfis_bimbo', css_class='form-control  col-md-6 mb-6'),
                css_class='form-row ', style='padding-bottom:90px;'
            ),
            Row(
                HTML('<div class="g-recaptcha" data-sitekey="6LdTmPUUAAAAAJHs1p_cn9ME_qOOw5264feotBNr" style="padding-bottom:30px;padding-right:40px;"></div>'),
                Column(Submit('submit', 'Salva'), css_class='form-control col-md-6 mb-6'),
                css_class='form-row col-md-8', style='padding-bottom:20px;'
            )
        )
