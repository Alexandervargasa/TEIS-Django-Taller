from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .infra.gateways import BancoNacionalProcesador
from .models import Libro
from .services import CompraRapidaService, CompraService
from .domain.logic import CalculadorImpuestos
from .infra.factories import PaymentFactory
from django.contrib.auth.models import User

class CompraView(View):
    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()

        try:
            libro = get_object_or_404(Libro, id=libro_id)

            usuario = User.objects.first()
            lista_productos = [libro]
            direccion = "Direccion Demo"

            mensaje = servicio.ejecutar_proceso_compra(usuario, lista_productos, direccion)

            return render(request, self.template_name, {
                "mensaje_exito": mensaje
            })

        except Exception as e:
            return render(request, self.template_name, {"error": str(e)}, status=400)

class CompraRapidaView(View):
    template_name = "tienda_app/compra_rapida.html"

    def get(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        return render(request, self.template_name, {
            "libro": libro,
            "total": total
        })

    def post(self, request, libro_id):
        servicio = CompraRapidaService(procesador_pago=BancoNacionalProcesador())

        try:
            total = servicio.procesar(libro_id)
            return HttpResponse(f"Compra exitosa: Total ${total}")
        except ValueError as e:
            return HttpResponse(str(e), status=400)