from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', views.caixa_view, name="home"),  # raiz vai para a tela do caixa
    path('clientes/', views.clientes_view, name="clientes"),
    path('planos/', views.planos_view, name="planos"),
    path('caixa/', views.caixa_view, name="caixa"),
]