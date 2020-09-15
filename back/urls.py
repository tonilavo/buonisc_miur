from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views 
from . import  backviews
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'ingressi', backviews.IngressiViewSet)
router.register(r'domande', backviews.DomandeViewSet)
router.register(r'admindomande', backviews.DomandeAdminViewSet)
router.register(r'allegati', backviews.AllegatiViewSet)

urlpatterns = [
	path('api/', include(router.urls)),
    path('accounts/', include('django.contrib.auth.urls')),    
    re_path(r'^login/$', auth_views.LoginView.as_view()),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(template_name='after_logout.html')),
    path('servizio', backviews.menu_servizio),
	path('ingressilist', backviews.lista_ingressi),
	path('domandelist', backviews.lista_domande),
    path('admindomandelist', backviews.adm_lista_domande),
    path('allegatilist', backviews.lista_allegati),
    path('preform_edit/<int:id>/', backviews.preform_edit),
	path('preform_annulla/<int:id>/', backviews.preform_annulla),
	path('preform_del/<int:id>/', backviews.preform_del),
    path('uploadB_domanda/<int:id>/', backviews.uploadb_file),
	path('updateB_domanda/<int:id>/', backviews.updateB_domanda),
 	path('reviewB_domanda/<int:id>/', backviews.reviewB_domanda),
    path('del_domanda/<int:id>/', backviews.del_domanda),
    path('riapri_domanda/<int:id>/', backviews.riapri_domanda),
    path('conferma_domanda/<int:id>/', backviews.conferma_domanda),
    path('send_domandanonvalida/<int:id>/', backviews.send_domandanonvalida),    
    re_path(r'^prep_email/$',  backviews.prep_email), 
    re_path(r'^resend_email/$', backviews.resend_email),   
]