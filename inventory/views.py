import requests
import logging
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

logger = logging.getLogger(__name__)

EXCHANGE_RATE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'
PROFIT_MARGIN = Decimal('0.40')
LOCAL_CURRENCY = 'VES'

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver y editar libros.
    """
    serializer_class = BookSerializer

    def get_queryset(self):
        """
        Opcionalmente filtra los libros por categoría y stock bajo (low-stock) usando parámetros de consulta.
        """
        queryset = Book.objects.all()
        
        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(category__iexact=category)

        threshold = self.request.query_params.get('threshold')
        if threshold is not None:
            try:
                threshold_int = int(threshold)
                queryset = queryset.filter(stock_quantity__lte=threshold_int)
            except ValueError:
                pass
        return queryset.order_by('id')

    @action(detail=True, methods=['post'], url_path='calculate-price')
    def calculate_price(self, request, pk=None):
        """
        Calcula y actualiza el precio de venta en moneda local basado en el costo en USD.
        Devuelve un error 503 si el servicio de tasas de cambio no está disponible.
        """
        book = self.get_object()
        
        try:
            response = requests.get(EXCHANGE_RATE_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            rate_from_api = data.get('rates', {}).get(LOCAL_CURRENCY)

            if not rate_from_api:
                logger.error(f"La moneda '{LOCAL_CURRENCY}' no fue encontrada en la respuesta de la API.")
                return Response(
                    {"error": f"La moneda '{LOCAL_CURRENCY}' no es soportada por el servicio de cambio."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            exchange_rate = Decimal(str(rate_from_api))

        except requests.RequestException as e:
            logger.error(f"La API de cambio de moneda falló. Error: {e}")
            return Response(
                {"error": "El servicio de tasas de cambio no está disponible en este momento. Por favor, inténtelo de nuevo más tarde."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        cost_local = book.cost_usd * exchange_rate
        margin_amount = cost_local * PROFIT_MARGIN
        selling_price = cost_local + margin_amount

        book.selling_price_local = selling_price
        book.save()

        response_data = {
            'book_id': book.id,
            'title': book.title,
            'cost_usd': book.cost_usd,
            'exchange_rate': exchange_rate,
            'cost_local': cost_local.quantize(Decimal('0.01')),
            'margin_percentage': int(PROFIT_MARGIN * 100),
            'selling_price_local': selling_price.quantize(Decimal('0.01')),
            'currency': LOCAL_CURRENCY,
            'calculation_timestamp': book.updated_at
        }
        
        return Response(response_data, status=status.HTTP_200_OK)