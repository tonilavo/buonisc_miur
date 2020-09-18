from django.db import models
from localflavor.generic.models import IBANField
from localflavor.generic.countries.sepa import IBAN_SEPA_COUNTRIES
from  datetime import date

# Create your models here.
class Ingressi(models.Model):
    id=models.AutoField(primary_key=True)
    data_ingresso = models.DateField(blank=False, null=False, default=date.today )
    codice_fiscale = models.CharField( max_length=16, blank=False, null=False)
    codfis_bimbo = models.CharField( max_length=16, blank=False, null=False)
    tel = models.CharField( max_length=60, blank=False, null=False)
    email = models.EmailField(blank=False, null=False, default="    @    ")
    stato = models.SmallIntegerField(blank=False, null=False, default=0)
    token = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        db_table = 'Ingressi'

class Domande(models.Model):
    id=models.AutoField(primary_key=True)
    token = models.CharField(max_length=60, blank=False, null=False)
    pr_data_richiesta = models.DateField(blank=False, null=False, default=date.today() )
    so_cod_fis = models.CharField(max_length=16, blank=False, null=False)
    so_cognome = models.CharField(max_length=50, blank=False, null=False)
    so_nome = models.CharField(max_length=36, blank=False, null=False)
    so_sesso = models.CharField(max_length=1, blank=False, null=False)
    so_nasc_dt = models.DateField(blank=False, null=False)
    so_nasc_com = models.CharField(max_length=28, blank=False, null=False)
    so_flag_residente = models.SmallIntegerField( blank=False, null=False)
    so_domicilio = models.CharField(max_length=150, blank=True, null=True)
    so_email = models.EmailField( blank=False, null=False)
    so_tel = models.CharField( max_length=30, blank=True, null=True)
    pr_cognome = models.CharField(max_length=24, blank=False, null=False)
    pr_nome = models.CharField(max_length=36, blank=False, null=False)
    pr_sesso = models.CharField(max_length=1, blank=False, null=False)
    pr_codfiscale = models.CharField(max_length=16, blank=False, null=False)
    pr_nasc_dt = models.DateField(blank=False, null=False)
    pr_nasc_com = models.CharField(max_length=25, blank=False, null=False)
    pr_fascia_asilo = models.CharField(max_length=1, blank=False, null=False)
    pr_tipo_asilo = models.CharField(max_length=1, blank=False, null=False)
    so_risc_diretta = models.CharField(max_length=1, blank=False, null=False)
    so_banca_iban = IBANField(include_countries=IBAN_SEPA_COUNTRIES, blank=True, null=True)
    pr_isee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pr_prot_isee_inps = models.CharField(max_length=27, blank=True, null=True)
    pr_data_isee_inps = models.DateField(blank=True, null=True)
    pr_spesa_mese = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    pr_spesa_totale = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    pr_mesi_frequenza = models.SmallIntegerField(blank=False, null=False, default=0)
    pr_imp_buoniscuola = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pr_imp_buoniinps = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pr_num_tot_ricevute = models.SmallIntegerField(blank=True, null=True, default=0)
    pr_importo_tot_ricevute = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pr_stato = models.SmallIntegerField(blank=True, null=True, default=0)

    class Meta:
        #managed = False
        db_table = 'domande'
        ordering = ['pr_data_richiesta']

    def __str__(self):
            return "%s-%s" % (self.id, self.pr_cognome + ' ' + self.pr_nome)

class Allegati(models.Model):
    id=models.AutoField(primary_key=True)
    domanda_num = models.IntegerField(blank=False, null=False)
    descrizione = models.CharField(max_length=65, blank=False,null=False)
    file = models.FileField(blank=False,null=False)

    class Meta:
        #managed = False
        db_table = 'allegati'
