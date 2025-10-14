from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer

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