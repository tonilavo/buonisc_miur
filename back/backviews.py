from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from front.tasks import *
from front.forms import *
from front.domande_forms import *
from front.models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .serializers import *
from .adminserializers import *
from rest_framework import viewsets

@login_required()
def preform_edit(request, id):

    rec= Ingressi.objects.get(pk=id)

    if request.method=='GET':
        form=CrispyPreForm(instance=rec)
    else:
        form=CrispyPreForm(request.POST, instance=rec)
        if form.is_valid():
            form.save()
            return redirect("/back/ingressilist")

    context = {'form': form}
    return render(request, 'preform.html', context)

# Legenda degli stati
#	stato = 5 per indicare annullata per dati DSU errati
#   stato = 6 per indicare annullata per doppio inserimento senza comunicazione


@login_required()
def preform_del(request, id):
    try:
        rec = Ingressi.objects.get(pk = id)

    except ObjectDoesNotExist:
        raise Http404('Record inesistente')

	#annullamento senza email
    rec.stato=6
    rec.save()
    return redirect("/back/ingressilist")

@login_required()
def lista_ingressi(request):

    recs=Ingressi.objects.all().order_by('-data_ingresso')
    context = { 'lista': recs}
    return render(request, 'ingressilist.html', context)

@login_required()
def lista_allegati(request):

    recs=Allegati.objects.all().order_by('domanda_num')
    context = { 'lista': recs}
    return render(request, 'allegatilist.html', context)

@login_required()
def get_pratiche_utente(request):
	if request.method=='GET':
		id = request.GET['id']
		#dal token passato via email si risale al'ingresso precedente e si recuperano i dati precompilati
		ingresso_ut=Ingressi.objects.get(pk=id)
		domande_ut=Domande.objects.filter(so_cod_fis=ingresso_ut.codice_fiscale)
		if domande_ut.count()>0:
			context = { 'lista': domande_ut}
			return render(request, 'domandelist.html', context)
		else:
    			return redirect('/back/ingressilist')


@login_required()
def lista_domande(request):

    recs=Domande.objects.all()
    context = { 'lista': recs}
    return render(request, 'domandelist.html', context)

@login_required()
def adm_lista_domande(request):

    recs=Domande.objects.all()
    context = { 'lista': recs}
    return render(request, 'admindomandelist.html', context)


@login_required()
def updateB_domanda(request, id):

	rec= Domande.objects.get(pk=id)

	asilorec=Asili.objects.get(pk=rec.pr_asilo.id)

	if request.method=='GET':
		campi_nodb = {'seltipoasilo': rec.pr_tipo_asilo, 'selasilo': asilorec.id}

		form =  CrispyDomandaForm( initial=campi_nodb, instance=rec)
	else:
		form = CrispyDomandaForm(request.POST, instance=rec)
		if form.is_valid():
			domandaform=form.save(commit=False)
			if domandaform.so_risc_diretta == 'S':
						domandaform.so_banca_iban=''

			domandaform.save()

			#rifacciamo vedere i dati in formato lettura
			return redirect('/back/domandelist')

	context = {'form': form}
	return render(request, 'backinsert_domanda.html', context)

@login_required()
def del_domanda(request, id):
	rec= Domande.objects.get(pk=id)
	rec.pr_stato=5 #cestinata
	rec.save()
	return redirect('/back/domandelist')


@login_required()
def riapri_domanda(request, id):
	rec= Domande.objects.get(pk=id)
	rec.pr_stato=0
	rec.save()
	return redirect('/back/domandelist')

@login_required()
def conferma_domanda(request, id):
	rec= Domande.objects.get(pk=id)
	if rec.pr_stato == 1:
		rec.pr_stato=2
		rec.save()
	return redirect('/back/domandelist')

@login_required()
def send_domandanonvalida(request, id):
	send_msg_domandanonvalida(id)
	return redirect('/back/domandelist')

@login_required()
def menu_servizio(request):
	return render(request, 'menu-backoffice.html')

def prep_email(request):
    if 'id'  in request.GET  :
        rec=Ingressi.objects.get(pk=request.GET['id'])
		#stato=1 significa in attesa di invio email
        rec.stato=1
        rec.save()
        send_link_form(request.GET['id'])
        return redirect("/back/ingressilist")
    else:
        return HttpResponse("Parametri insufficienti")

def resend_email(request):
    if 'id'  in request.GET  :
        resend_link_form(request.GET['id'])
        return redirect("/back/ingressilist")
    else:
        return HttpResponse("Parametri insufficienti")


@login_required()
def reviewB_domanda(request, id):
	rec= Domande.objects.get(pk=id)

	context = {'data': rec, 'id': id}

    # visualizzo anche gli allegati se ci sono
	photos_list = Allegati.objects.filter(domanda_num = id)
	if photos_list.count()>0:
		context['photos']=photos_list

	if request.method=='POST':
		request.session['last_url']='review_domanda'
		if 'edit' in request.POST:
			next_url=  '/back/updateB_domanda/' + str(id) +'/'
			return HttpResponseRedirect(next_url)

		else:  #premuto conferma finale
				next_url="/back/domandelist"
				return HttpResponseRedirect(next_url)

	return render(request, 'rivedi_domandaB.html', context)

class IngressiViewSet(viewsets.ModelViewSet):
    queryset = Ingressi.objects.all().reverse()
    serializer_class = IngressiSerializer

class DomandeViewSet(viewsets.ModelViewSet):
    queryset = Domande.objects.all()
    serializer_class = DomandeSerializer

class DomandeAdminViewSet(viewsets.ModelViewSet):
    queryset = Domande.objects.all()
    serializer_class = AdminDomandeSerializer

class AllegatiViewSet(viewsets.ModelViewSet):
    queryset = Allegati.objects.all().order_by('domanda_num')
    serializer_class = AllegatiSerializer


@login_required()
def uploadb_file(request, id):

	form = None
	if request.method == 'POST':
		if 'carica' in request.POST:
			form = PhotoForm(request.POST, request.FILES)

			if form.is_valid():
				rec_allegato = {}
				rec_allegato['domanda_num'] = id
				rec_allegato['file'] = 'all' + form.cleaned_data['file']
				rec_allegato['descrizione'] = form.cleaned_data['descrizione']
				Allegati.objects.create(**rec_allegato)

				next_url = '/back/uploadB_domanda/' + str(id) + '/'
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

	next_url ='/back/domandelist/'
	url_clear_allfiles ='/clear_files/' + str(id) + '/'
	photos_list = Allegati.objects.filter(domanda_num=id)
	context = {'form': form, 'photos': photos_list, 'url_ritorno': next_url, 'url_deleteall': url_clear_allfiles}

	return render(request, 'massivo.html', context)
