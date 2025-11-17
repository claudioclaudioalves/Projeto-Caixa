from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Plano, Movimento
from django.utils import timezone
from django.contrib import messages
import pytz

LOCAL_TZ = pytz.timezone("America/Sao_Paulo")


def clientes_view(request):
    planos = Plano.objects.all()
    clientes = Cliente.objects.all()
    cliente_para_editar = None

    if request.method == "POST":
        cliente_id = request.POST.get("cliente_id")
        plano_id = request.POST.get("plano_id")
        nome = request.POST.get("nome")
        placa = request.POST.get("placa")

        placa_maiuscula = placa.strip().upper() if placa else None 

        if "deletar" in request.POST and cliente_id:
            Cliente.objects.filter(id=cliente_id).delete()
            return redirect("clientes")

        if cliente_id and not "deletar" in request.POST:
            cliente = Cliente.objects.get(id=cliente_id)
            cliente.nome = nome  # Linha adicionada para editar o nome
            cliente.placa = placa_maiuscula
            if plano_id:
                cliente.plano = Plano.objects.get(id=plano_id)
            cliente.save()

        elif nome:
            cliente = Cliente.objects.create(
                nome=nome,
                placa=placa_maiuscula,
                plano=Plano.objects.get(id=plano_id) if plano_id else None
            )

        return redirect("clientes")

    cliente_edit_id = request.GET.get("editar")
    if cliente_edit_id:
        cliente_para_editar = Cliente.objects.get(id=cliente_edit_id)

    return render(request, "operacao/clientes.html", {
        "clientes": clientes,
        "planos": planos,
        "cliente_para_editar": cliente_para_editar
    })


def planos_view(request):
    if request.method == "POST":
        plano_id = request.POST.get("plano_id") 
        nome = request.POST.get("nome")
        valor = request.POST.get("valor")

        
        
        if request.POST.get("deletar") == "true" and plano_id:
            plano = get_object_or_404(Plano, id=plano_id)
            plano.delete()
            return redirect("planos")

        
        if nome and valor:
            Plano.objects.create(nome=nome, valor=valor)
        
        return redirect("planos")

    planos = Plano.objects.all()
    return render(request, "operacao/planos.html", {"planos": planos})


def caixa_view(request):
    movimentos = Movimento.objects.filter(ativo=True)
    clientes_no_patio_count = movimentos.count()
    clientes_placas = Cliente.objects.values('nome', 'placa') 
    
    if request.method == "POST":
        
        if "entrada" in request.POST:
            placa_digitada = request.POST.get("placa").strip().upper() 

            try:
                cliente = Cliente.objects.get(placa=placa_digitada)
            except Cliente.DoesNotExist:
                messages.error(request, f"Nenhum cliente encontrado com a placa {placa_digitada}")
                return redirect("caixa")

            movimento_ativo_mensalista = Movimento.objects.filter(
                placa=placa_digitada, 
                ativo=True,
                cliente__plano__isnull=False
            ).exists()

            if movimento_ativo_mensalista:
                messages.error(
                    request,
                    f"ERRO: O cliente {cliente.nome} (Placa: {placa_digitada}) já está registrado no pátio. Registre a saída primeiro."
                )
            else:
                movimento = Movimento.objects.create(cliente=cliente, placa=placa_digitada)
                hora_entrada_local = movimento.hora_entrada.astimezone(LOCAL_TZ).strftime("%d/%m/%Y - %H:%M")
                messages.success(
                    request,
                    f"Entrada registrada: {cliente.nome} - {cliente.plano.nome if cliente.plano else 'Sem plano'} - Entrada: {hora_entrada_local}"
                )

        elif "entrada_avulso" in request.POST:
            placa_avulso_digitada = request.POST.get("placa_avulso", "").strip().upper() 
            tempo_horas = int(request.POST.get("tempo_horas"))
            forma_pagamento = request.POST.get("forma_pagamento")
            
            valor = 5 if tempo_horas == 1 else 10

            movimento = Movimento.objects.create(
                cliente=None, 
                placa=placa_avulso_digitada,
                valor_cobrado=valor,
                forma_pagamento=forma_pagamento,
            )
            
            hora_entrada_local = movimento.hora_entrada.astimezone(LOCAL_TZ).strftime("%d/%m/%Y - %H:%M")
            messages.success(
                request,
                f"Entrada avulsa registrada: Placa {placa_avulso_digitada} - R$ {valor} via {forma_pagamento} - Entrada: {hora_entrada_local}"
            )

        elif "saida" in request.POST:
            movimento_id = request.POST.get("movimento_id")
            movimento = Movimento.objects.get(id=movimento_id)
            movimento.hora_saida = timezone.now()
            movimento.ativo = False
            movimento.save()
            
            nome_cliente = movimento.cliente.nome if movimento.cliente else "Cliente Avulso"
            
            hora_saida_local = movimento.hora_saida.astimezone(LOCAL_TZ).strftime("%d/%m/%Y - %H:%M")
            messages.success(
                request,
                f"Saída registrada: {nome_cliente} - Saída: {hora_saida_local}"
            )

        return redirect("caixa")

    for m in movimentos:
        m.hora_entrada_local = m.hora_entrada.astimezone(LOCAL_TZ).strftime("%d/%m/%Y - %H:%M")
        
        if m.cliente:
            m.nome_display = m.cliente.nome
            m.plano_display = m.cliente.plano.nome if m.cliente.plano else "--"
        else:
            m.nome_display = "Avulso" 
            m.plano_display = "--"

    return render(request, "operacao/caixa.html", {
        "movimentos": movimentos,
        "clientes_placas": clientes_placas,
        "clientes_no_patio_count": clientes_no_patio_count
    })