from django.urls import path

from . import views

app_name = 'joseph'
urlpatterns = [
    path('', views.Index, name='index')
]