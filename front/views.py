from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from .tasks import *
from .forms import *
from .domande_forms import *
from .models import *
#from rest_framework import viewsets
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages import get_messages
from codicefiscale import codicefiscale
import random
import datetime
import requests

def get_url_prefix():
	if settings.USE_ABSOLUTE_PATH == 'True':
		if settings.HOSTNAME[0:7] != "http://":
			hostname = "http://" + settings.HOSTNAME
		else:
			hostname = settings.HOSTNAME

		return hostname
	else:
		return '/front'
# Create your views here.
def preform_insert(request):
	dt_scadenza = datetime.datetime.strptime(settings.DATA_SCADENZA, "%d/%m/%Y").date()

	if timezone.now().date() > dt_scadenza:
		context = {'scadenza': settings.DATA_SCADENZA}
		return render(request, 'preform_fine.html', context)

	if request.method == 'GET':
		form = CrispyPreForm()
	else:
		form = CrispyPreForm(request.POST)
		if form.is_valid():
			preform = form.save(commit=False)
			preform.data_ingresso = timezone.now()
			preform.save()
			send_link_form(preform.pk)
			# visualizza messaggio di conferma all'utente
			return render(request, 'response.html')

	context = {'form': form}
	return render(request, 'preform.html', context)


def preform_insert_captcha(request):
	dt_scadenza = datetime.datetime.strptime(settings.DATA_SCADENZA, "%d/%m/%Y").date()

	if timezone.now().date() > dt_scadenza:
		context = {'scadenza': settings.DATA_SCADENZA}
		return render(request, 'preform_fine.html', context)

	if request.method == 'GET':
		form = CrispyPreForm()
	else:
		form = CrispyPreForm(request.POST)
		if form.is_valid():
			recaptcha_response = request.POST.get('g-recaptcha-response')
			data = {
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': recaptcha_response
            }
			r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
			result = r.json()
			print(result)
			''' End reCAPTCHA validation '''

			if result['success']:
				preform = form.save(commit=False)
				preform.data_ingresso = timezone.now()
				preform.save()
				send_link_form(preform.pk)
				# visualizza messaggio di conferma all'utente
				return render(request, 'response.html')
			else:
				messages.error(request, 'reCAPTCHA non valido. Ritentare.')

	context = {'form': form}
	return render(request, 'preform.html', context)

# ********************************************************************************************************
#               INSERT_DOMANDA
# ********************************************************************************************************
def insert_domanda(request):
	domandaform = None
	if request.method == 'GET':
		if 'token' not in request.GET:
			msg = 'Utente non autorizzato. Impossibile continuare'
			context = {'errmessage': msg}
			return render(request, "errormessages.html", context)

		mytoken = request.GET['token']
		if settings.DEBUG:
			print("token: " + mytoken)
		request.session['token'] = mytoken
		request.session['domanda_id'] = None
		# ricerca la domanda collegata al token
		rec_domanda = Domande.objects.filter(token=mytoken)
		nDomande = rec_domanda.count()

		if nDomande == 1:  # se il record con quel token già esiste si va in update
			rec = rec_domanda[0]
			if settings.DEBUG:
				print("domanda trovata. Id:" + str(id) + " stato:"+  str(rec.pr_stato))
				print("token in  sessione:"+ request.session['token'])
			# dallo stato della domanda decido se cosa può fare l'utente
			if rec.pr_stato <= 1 :
				request.session['domanda_id'] = rec.id
				next_url = get_url_prefix() + '/review_domanda/' + str(rec.id) + '/'
				if settings.DEBUG:
					print("redirect to " + next_url)
				return HttpResponseRedirect(next_url)
			elif (rec.pr_stato == 2):  # domanda confermata dall'ufficio
				msg = 'La  domanda con id.' + str(rec.id) + ' è già stata verificata e archiviata.'
				context = {'errmessage': msg}
				return render(request, "errormessages.html", context)
			elif (rec.pr_stato > 4):  # domanda annullata dall'ufficio
				msg = 'La  domanda con id.' + str(rec.id) + ' è già stata controllata e annullata per dati non corretti.'
				context = {'errmessage': msg}
				return render(request, "errormessages.html", context)

		elif nDomande == 0:  # la prima volta che l'utente accede con quel token va creato un record per la domanda
			# dal token passato in Get si risale all'ingresso corrispondente e si recuperano i dati precompilati
			ingressi = Ingressi.objects.filter(token=mytoken)

			if ingressi.count() == 1:  # trovato l'ingresso corrispondente
				rec = ingressi[0]
				cod_fiscale = rec.codice_fiscale
				anag_richiedente = get_ana_apk(cod_fiscale)
				cognome_ric=''
				nome_ric=''
				dtnascita_ric=None
				comuneNascita_ric=''
				indirizzo_ric=''

				if anag_richiedente:
					cognome_ric = anag_richiedente['cognome']
					nome_ric = anag_richiedente['nome']
					dtnascita_ric = anag_richiedente['data_nascita']
					comuneNascita_ric=anag_richiedente['comune_nascita']
					indirizzo_ric=anag_richiedente['indirizzo']

				if int(cod_fiscale[9:11])>31:
					sex_ric='F'
				else:
					sex_ric ='M'

				cod_fiscale = rec.codfis_bimbo
				anag_minore = get_ana_apk(cod_fiscale)
				cognome_minore=''
				nome_minore=''
				dtnascita_minore=None
				luogo_nascita_minore=''

				if anag_minore:
					cognome_minore = anag_minore['cognome']
					nome_minore = anag_minore['nome']
					dtnascita_minore = anag_minore['data_nascita']
					luogo_nascita_minore=anag_minore['comune_nascita']

				if int(cod_fiscale[9:11])>31:
					sex_minore='F'
				else:
					sex_minore ='M'

				form = CrispyDomandaForm(
						initial={'token': mytoken, 'pr_data_richiesta': timezone.now().date,
							 'so_cod_fis': rec.codice_fiscale, 'so_cognome': cognome_ric,
							 'so_nome': nome_ric, 'so_sesso': sex_ric,
							 'so_nasc_dt': dtnascita_ric, 'so_nasc_com': comuneNascita_ric,
							 'so_tel': rec.tel, 'so_email': rec.email, 'so_risc_diretta': 'S',
							 'pr_cognome': cognome_minore, 'pr_nome': nome_minore, 'pr_sesso': sex_minore,
                             'pr_prot_isee_inps': 'INPS-ISEE-2020-', 'pr_codfiscale': rec.codfis_bimbo,
							 'pr_nasc_dt': dtnascita_minore, 'pr_nasc_com': luogo_nascita_minore,
							 'pr_fascia_asilo':'M', 'pr_tipo_asilo': 'C'})

			else:  # token sconosciuto
				msg = 'Utente non autorizzato. Impossibile continuare'
				context = {'errmessage': msg}
				return render(request, "errormessages.html", context)
	else:
		# Post dopo premuto Salva
		form = CrispyDomandaForm(request.POST)
		form_ok = form.is_valid()
		if form_ok:
			domandaform = form.save(commit=False)

			# si aggiorna il record con i dati dai campi non Db
			# si leggono i valori da campi non db per tipo e asilo  e si scrivono nei campi db
			# si trova il record  di Asili da legare in FK

			#	si toglie l'iban farlocco messo all'inizio per passare il clean
			if domandaform.so_risc_diretta == 'S':
				domandaform.so_banca_iban = ''
			domandaform.save()
			# ripresento in lettura i dati  all'utente
			next_url = get_url_prefix() + '/review_domanda/' + str(domandaform.pk) + '/'
			if settings.DEBUG:
				print("redirect to " + next_url)
			return HttpResponseRedirect(next_url)

	context = {'form': form}
	return render(request, 'insert_domanda.html', context)

# ********************************************************************************************************
#               UPDATE_DOMANDA
# ********************************************************************************************************
def update_domanda(request, id):
	# controllo che  il token della domanda sia in sessione
	if 'token'  in request.session:
    		mytoken = request.session['token']
	else:
		msg = 'Utente non autorizzato. Impossibile continuare'
		context = {'errmessage': msg}
		return render(request, "errormessages.html", context)

	try:
		rec = Domande.objects.get(pk=id)

	except:
		msg = 'Domanda con Id.'+str(id) + 'inesistente'
		context = {'errmessage': msg}
		return render(request, "errormessages.html", context)

	if request.method == 'GET':
		form = CrispyDomandaForm(instance=rec)
		if settings.DEBUG:
			print("form in GET")
	else:
		# Post dopo premuto Salva
		form = CrispyDomandaForm(request.POST, instance=rec)

		form_ok = form.is_valid()
		if form_ok:
			domandaform = form.save(commit=False)

			# si aggiorna il record con i dati dai campi non Db
			# si leggono i valori da campi non db per tipo e asilo  e si scrivono nei campi db
			# si trova il record  di Asili da legare in FK
			#	si toglie l'iban farlocco messo all'inizio per passare il clean
			if domandaform.so_risc_diretta == 'S':
				domandaform.so_banca_iban = ''
			domandaform.save()
			# ripresento in lettura i dati  all'utente
			next_url = get_url_prefix() + '/review_domanda/' + str(domandaform.pk) + '/'
			if settings.DEBUG:
				print("redirect to " + next_url)
			return HttpResponseRedirect(next_url)

		else:
			if settings.DEBUG:
				print(form.errors.as_data())
			context = {'form': form}
			return render(request, 'insert_domanda.html', context)

		# rifacciamo vedere i dati in sola lettura all'utente
		request.session['token'] = mytoken
		next_url = get_url_prefix() + '/review_domanda/' + str(id) + '/'
		if settings.DEBUG:
			print("da update_domanda redirect to " + next_url)

		return HttpResponseRedirect(next_url)

	context = {'form': form}
	return render(request, 'insert_domanda.html', context)


# ********************************************************************************************************
#               REVIEW_DOMANDA
# ********************************************************************************************************
def review_domanda(request, id):
	if 'token'  in request.session:
		mytoken = request.session['token']
	else:
		msg = 'Utente non autorizzato. Impossibile continuare'
		context = {'errmessage': msg}
		return render(request, "errormessages.html", context)

	if settings.DEBUG:
		print("domanda review. Id:" + str(id))
		print("token in  sessione:"+ mytoken + 'len:'+str(len(mytoken)))

	try:
		rec = Domande.objects.get(pk=id)
	except:
		msg = 'Domanda con Id.' + str(id) + 'inesistente'
		context = {'errmessage': msg}
		return render(request, "errormessages.html", context)

	if rec.pr_stato != 0:
		msg = 'Domanda già confermata ed archiviata'
		context = {'errmessage': msg}
		return render(request, "errormessages.html", context)

	context = {'data': rec,  'id': id}

	# visualizzo anche gli allegati se ci sono
	photos_list = Allegati.objects.filter(domanda_num=id)
	if photos_list.count() > 0:
		context['photos'] = photos_list

	if request.method == 'POST':
		request.session['last_url'] = 'review_domanda'
		if 'edit' in request.POST:
			next_url = get_url_prefix() + '/update_domanda/' + str(id) + '/'
			if settings.DEBUG:
				print("redirect to " + next_url)
			return HttpResponseRedirect(next_url)

		elif 'addfiles' in request.POST:

			next_url = get_url_prefix() + '/upload/' + str(id) + '/'
			if settings.DEBUG:
				print("redirect to " + next_url)
			return HttpResponseRedirect(next_url)

		else:  # premuto conferma finale
			context = {'data': rec,  'id': id}

			if rec.pr_tipo_asilo =='P':
				result = check_finale(id)
			else:
				result = 'OK'

			if result != 'OK':
				mess = {result, }
				context['messages'] = mess
				return render(request, 'rivedi_domanda.html', context)
			else:
				# mettendo stato a 1 significa che l'utente ha confermato e inviato la domanda
				rec.pr_stato = 1
				rec.save()
				# il riepilogo della domanda viene inviato via email
				send_riep_domanda(rec.so_email, rec.pk)

				next_url = get_url_prefix() + '/msgfinale/' + str(id)

				if settings.DEBUG:
					print("redirect to " + next_url)
				return HttpResponseRedirect(next_url)

	return render(request, 'rivedi_domanda.html', context)


def check_finale(id):

	rec = Domande.objects.get(pk=id)
	if rec.pr_num_tot_ricevute > 0 and rec.pr_tipo_asilo == 'P':
		# controlla la presenza di tanti allegati quanto indicato nel campo
		num_allegati = Allegati.objects.filter(domanda_num=id).count()
		if num_allegati != rec.pr_num_tot_ricevute:
			return "Nella domanda ha specificato num.ricevute allegate:" + str(rec.pr_num_tot_ricevute) + ' mentre i file caricati sono in numero '+str(num_allegati)
	return "OK"

class BasicUploadView(View):
	def get(self, request):
		if true:
			# if request.session['domanda_id']:
			# domanda_num = request.session['domanda_id']

			photos_list = Allegati.objects.filter(domanda_num=domanda_num)
			context = {'photos': photos_list}
			return render(self.request, 'upload.html', context)
		else:
			return HttpResponse('Non sei autorizzato la caricamento allegati')

	def post(self, request):

		form = PhotoForm(self.request.POST, self.request.FILES)
		if form.is_valid():
			photo = form.save(commit=False)
			photo.data_inserimento = timezone.now()
			print("foto salvata per domanda num." + str(request.session['domanda_id']))
			photo.domanda_num = request.session['domanda_id']
			photo.save()
			print("url:" + photo.file.url)
			data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
		else:
			data = {'is_valid': False}
		return JsonResponse(data)


def handle_uploaded_file(f):
	with open('tmp/' + randomString(11), 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)
import string

def randomString(stringLength):
	letters = string.ascii_letters
	return ''.join(random.choice(letters) for i in range(stringLength))

# ********************************************************************************************************
#               UPLOAD_FILE
# ********************************************************************************************************
def upload_file(request, id):
	# controllo che  il token della domanda sia in sessione
	if 'token'  in request.session:
    		mytoken = request.session['token']
	else:
		msg = 'Utente non autorizzato. Impossibile continuare'
		context = {'errmessage': msg}
		return render(request, "errormessages.html", context)

	form = None
	if request.method == 'POST':
		if 'carica' in request.POST:
			form = PhotoForm(request.POST, request.FILES)

			if form.is_valid():
				rec_allegato = {}
				rec_allegato['domanda_num'] = id
				rec_allegato['file'] = form.cleaned_data['file']
				rec_allegato['descrizione'] = form.cleaned_data['descrizione']
				Allegati.objects.create(**rec_allegato)

				next_url = get_url_prefix() + '/upload/' + str(id) + '/'
				if settings.DEBUG:
					print("redirect to " + next_url)

				return HttpResponseRedirect(next_url)

		elif 'clear' in request.POST:
			next_url = get_url_prefix() + '/clear_files/' + str(id) + '/'
			if settings.DEBUG:
				print("redirect to " + next_url)

			return HttpResponseRedirect(next_url)

	else:
		form = PhotoForm()

	next_url = get_url_prefix() + '/review_domanda/' + str(id) + '/'
	url_clear_allfiles = get_url_prefix() + '/clear_files/' + str(id) + '/'
	photos_list = Allegati.objects.filter(domanda_num=id)
	context = {'form': form, 'photos': photos_list, 'url_ritorno': next_url, 'url_deleteall': url_clear_allfiles}

	return render(request, 'massivo.html', context)
# ********************************************************************************************************
#                           CLEAR_DATABASE
# ********************************************************************************************************
def clear_database(request, id):
	# controllo che  il token della domanda sia in sessione
	if 'token'  in request.session:
    		mytoken = request.session['token']
	else:
		msg = 'Utente non autorizzato. Impossibile continuare'
		context = {'errmessage': msg}
		return render(request, "errormessages.html", context)

	for photo in Allegati.objects.filter(domanda_num=id):
		photo.file.delete()
		photo.delete()

	curr_url = get_url_prefix() + '/upload/' + str(id) + '/'
	photos_list = None
	context = {'form': PhotoForm(), 'photos': photos_list, 'url_ritorno': curr_url}
	return render(request, 'massivo.html', context)

def msgfinale(request, id):
	return render(request, "testmessages.html", {'id': id})

def domandatest(request):
	cf_test = 'BRGLWG73S24I726A'

	test_token = 'sd678766Gre$110Psss#ù'
	rec_prec = Ingressi.objects.filter(codice_fiscale=cf_test, token=test_token)
	if rec_prec.count() == 0:
		rec_prec = Ingressi.objects.create( email="tonino.lavorati@gmail.com", tel = "3939202022",
										    codice_fiscale=cf_test, token='BRGLWG73S24I726A', stato=0)
		rec_prec.save()
	request.session.flush()
	request.session['token'] = test_token

	testdomande_rec = Domande.objects.filter(pr_codfiscale='BRGRLA16S69E202I', token=test_token)
	if settings.DEBUG:
		print("trovati n."+str(testdomande_rec.count()) + " records")
	if testdomande_rec.count()==0:
		domanda_data = {}
		domanda_data['token'] = test_token
		domanda_data['pr_data_richiesta'] = timezone.now()
		domanda_data['so_cognome'] = 'BARGAGLI'
		domanda_data['so_nome'] = 'LUDWIG'
		domanda_data['so_nasc_dt'] = datetime.datetime(1973, 11, 24)
		domanda_data['so_nasc_com'] = 'SIENA'
		domanda_data['so_flag_residente'] = 1
		domanda_data['so_cod_fis'] = 'BRGLWG73S24I726A'
		domanda_data['so_sesso'] = 'M'
		domanda_data['so_email'] = rec_prec.email
		domanda_data['so_tel'] = rec_prec.tel
		domanda_data['pr_cognome'] = 'BARGAGLI'
		domanda_data['pr_nome'] = 'ARIEL'
		domanda_data['pr_sesso'] = 'F'
		domanda_data['pr_nasc_dt'] = datetime.datetime(2016, 11, 29)
		domanda_data['pr_nasc_com'] = 'GROSSETO'
		domanda_data['pr_codfiscale'] = 'BRGRLA16S69E202I'
		domanda_data['pr_fascia_asilo'] = 'M'
		domanda_data['pr_spesa_mese'] = 250
		domanda_data['pr_spesa_totale'] = 1250
		domanda_data['pr_tipo_asilo'] = 'P'
		domanda_data['so_risc_diretta'] = 'N'
		domanda_data['so_banca_iban'] = 'IT76M0301503200000000218501'
		domanda_data['so_risc_diretta'] = 'N'
		domanda_data['so_banca_iban'] = 'IT76M0301503200000000218501'
		domanda_data['pr_prot_isee_inps'] = 'INPS-ISEE-2020-'

		domanda_data['pr_importo_tot_ricevute'] = 1400
		rec = Domande.objects.create(**domanda_data)
		domanda_num = rec.pk
	else:
		domanda_num = testdomande_rec[0].pk

	return redirect(get_url_prefix() + '/update_domanda/' + str(domanda_num)+'/')

def get_ana_apk(cod_fiscale):
    dati_anag = None
    risp = requests.get( settings.APK_SERVICE + cod_fiscale)
    dato = risp.json()

    if dato['cognome']:
    	#	replica la domanda in Pratiche integrandola con la parte anagrafica e di residenza
    	#	rimetto in unica stringa i campi dell'indirizzo
        indirizzo = '' if dato['resDUG'] is None else dato['resDUG']
        indirizzo +=  '' if  dato['resDUF'] is None else ' ' + dato['resDUF']
        indirizzo +=  '' if dato['resCivico'] is None else ' ' + str(dato['resCivico'])

        str_dtaNascita = dato['dataNascita'][0:10]
        dtaNascita = datetime.datetime.strptime(str_dtaNascita, "%Y-%m-%d").date()
        dati_anag = {'cognome': dato['cognome'], 'nome': dato['nome'], 'cod_fiscale': cod_fiscale,  'data_nascita': dtaNascita,
                                        'comune_nascita': dato['comuneNascita'], 'prov': dato['provinciaNascita'], 'indirizzo': indirizzo, 'local':'GROSSETO', 'cap':58100, 'prov': 'GR'}

    return dati_anag
