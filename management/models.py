from django.db import models
from django.utils import timezone

class Plano(models.Model):
    nome = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    placa = models.CharField(max_length=20, blank=True, null=True)
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome

class Movimento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    placa = models.CharField(max_length=20)
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_saida = models.DateTimeField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    valor_cobrado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    forma_pagamento = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        if self.cliente:
            return f"{self.cliente.nome} - {self.placa}"
        return f"Cliente avulso - {self.placa}"
