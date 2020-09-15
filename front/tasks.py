from celery import shared_task
from time import sleep
from django.template.loader import render_to_string
from django.core.mail import send_mail
from access_tokens import scope, tokens
from .models import *
from .domande_forms import *
from django.conf import settings
import os

@shared_task
def sleepy(duration):
	sleep(duration)
	return None



@shared_task
def send_token(idIngresso):

	if settings.HOSTNAME[0:7]!= "http://":
		hostname = "http://" + settings.HOSTNAME
	else:
		hostname = settings.HOSTNAME

	token = tokens.generate(scope=(), key="", salt="None")
	#al momento di generare il token, questo viene salvato nel db per matcharlo con la richiesta di aprire il form della domanda
	rec=Ingressi.objects.get(pk=idIngresso)
	#stato=2 significa email inviata
	rec.stato=2
	rec.token=token
	rec.save()
	print("token generato per id:"+str(id)+ '='+ token)
	url_domanda =  hostname + '/domanda/?token='+token
	context = {'url_domanda': url_domanda}
	message_txt = render_to_string('email_to.txt',  context)
	print(message_txt)
	message_html = render_to_string('email_to.html',  context)
	print(message_html)
	send_mail("Comune di Grosseto - invio del token per la compilazione della richiesta di buoni MIUR per materne/nidi",
		message_txt,
        settings.EMAIL_HOST_USER,
		[rec.email],
		html_message=message_html)
	return None

@shared_task
def resend_token(idIngresso):
	if settings.HOSTNAME[0:7]!= "http://":
		hostname = "http://" + settings.HOSTNAME
	else:
		hostname = settings.HOSTNAME

	rec = Ingressi.objects.get(pk=idIngresso)
	url_domanda =  hostname + '/domanda/?token=' + rec.token
	context = {'url_domanda': url_domanda}
	message_txt = render_to_string('email_to.txt',  context)
	message_html = render_to_string('email_to.html',  context)
	print(message_html)
	send_mail("Comune di Grosseto - Reinvio del token per la compilazione della richiesta di buoni MIUR per materne/nidi",
		message_txt,
        settings.EMAIL_HOST_USER,
		[rec.email],
		html_message=message_html)
	return None

@shared_task
def send_msg_domandanonvalida(idDomanda):
	#si  annulla la richiesta per darti incorretti con email all'utente
	rec=Domande.objects.get(pk=idDomanda)
	user_email = rec.so_email
	#stato=0 significa aperta
	rec.pr_stato=0  #domand riaperta affinchè utente corregga errori
	rec.save()
	message_txt = render_to_string('annullamento.txt')
	message_html = render_to_string('annullamento.html')
	oggetto = 'Comune di Grosseto - comunicazione di non accoglimento della domanda per i Buoni MIUR'
	send_mail(oggetto,
		message_txt,
        settings.EMAIL_HOST_USER,
		[user_email],
		html_message=message_html)
	return None

@shared_task
def send_ok_preform(user_email):
	context = None
	message_txt = render_to_string('response.txt',  context)
	message_html = render_to_string('response.html',  context)
	print(message_html)
	oggetto = 'Comune di Grosseto - token inviato per la compilazione della richiesta di buoni MIUR'
	send_mail(oggetto,
		message_txt,
        settings.EMAIL_HOST_USER,
		[user_email],
		html_message=message_html)
	return None

@shared_task
def send_riep_domanda(user_email, id):
	rec= Domande.objects.get(pk=id)
	asilorec=Asili.objects.get(pk=rec.pr_asilo.id)

	form=Domandeform(instance=rec)

	context = {'form': form, 'asilo':asilorec.nome, 'id': id}
	print("task context")
	print(context)

	message_txt = render_to_string('conferma.txt',  context)
	message_html = render_to_string('conferma_domanda.html',  context)
	print(message_html)
	oggetto = 'Comune di Grosseto - riepilogo della richiesta di buoni MIUR num.2020/'+str(id)+ ' per il minore '+ rec.pr_cognome+ ' ' + rec.pr_nome
	send_mail(oggetto,
		message_txt,
        settings.EMAIL_HOST_USER,
		[user_email],
		[settings.EMAIL_HOST_USER],
		html_message=message_html)
	return None

def check_allegati():
	list_files_notexists = []
	for all in Allegati.objects.all():
		if not os.path.isfile(all.file.path):
			list_files_notexists.append(all.file.path)
	return(list_files_notexists)
