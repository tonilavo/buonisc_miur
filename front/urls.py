"""django_email URL Configuration

"""
from django.contrib import admin
from django.urls import path, re_path,  include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
	path('api/', include(router.urls)),
#	path('sitofermo', views.sito_fermo),
	path('predomanda/', views.preform_insert),
	path('update_domanda/<int:id>/', views.update_domanda),
	path('review_domanda/<int:id>/', views.review_domanda),
	re_path(r'^domanda/$', views.insert_domanda),
	path('domandatest/',  views.domandatest),
 	path('upload/<int:id>/', views.upload_file),
	path('msgfinale/<int:id>', views.msgfinale),
	path('clear_files/<int:id>/', views.clear_database, name='clear_database'),
]
