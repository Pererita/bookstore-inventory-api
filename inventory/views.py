from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los libros ser vistos o editados.
    """
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer