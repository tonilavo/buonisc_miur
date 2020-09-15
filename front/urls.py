"""django_email URL Configuration

"""
from django.contrib import admin
from django.urls import path, re_path,  include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
	path('api/', include(router.urls)),
]
