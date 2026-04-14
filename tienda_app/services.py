from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Inventario, Libro


class CompraService:
    def __init__(self, procesador_pago):
        self.procesador = procesador_pago
        self.builder = OrdenBuilder()
    
    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total_con_iva = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        return {
            "libro": libro,
            "total": total_con_iva
        }

    def ejecutar_proceso_compra(self, usuario, lista_productos,direccion):
    # Uso del Builder: Semantica clara y validacion interna
        orden = (self.builder
        .con_usuario(usuario)
        .con_productos(lista_productos)
        .para_envio(direccion)
        .build())

    # Uso del Factory (inyectado): Cambio de comportamiento sin cambio de codigo
        if self.procesador.pagar(orden.total):
            return f"Orden {orden.id} procesada exitosamente."
        
        orden.delete()
        raise Exception("Error en la pasarela de pagos.")

class CompraRapidaService:
    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def procesar(self, libro_id):
        libro = Libro.objects.get(id=libro_id)
        inv = Inventario.objects.get(libro=libro)

        if inv.cantidad <= 0:
            raise ValueError("No hay existencias.")

        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        if self.procesador_pago.pagar(total):
            inv.cantidad -= 1
            inv.save()
            return total

        return None