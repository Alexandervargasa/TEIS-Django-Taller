from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import OrdenInputSerializer
from tienda_app.services import CompraRapidaService
from tienda_app.infra.factories import PaymentFactory

class CompraAPIView(APIView):
    """
    Endpoint para procesar compras vía JSON.
    POST /api/v1/comprar/
    Body: { "libro_id": 1, "direccion_envio": "Calle 123" }
    """

    def post(self, request):
        # 1. Validar el JSON entrante
        serializer = OrdenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data

        try:
            # 2. Factory decide qué procesador usar
            gateway = PaymentFactory.get_processor()

            # 3. Servicio ejecuta la lógica de negocio
            servicio = CompraRapidaService(procesador_pago=gateway)
            total = servicio.procesar(libro_id=datos['libro_id'])

            return Response(
                {"estado": "exito", "mensaje": f"Orden creada. Total: {total}"},
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            # Sin stock o libro no existe
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)

        except Exception as e:
            return Response({"error": "Error interno"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)