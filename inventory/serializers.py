from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Book.
    """
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'isbn',
            'cost_usd',
            'selling_price_local',
            'stock_quantity',
            'category',
            'supplier_country',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'selling_price_local',
            'created_at',
            'updated_at'
        ]

    def validate_cost_usd(self, value):
        """
        Comprueba que el costo en USD sea mayor a cero.
        """
        if value <= 0:
            raise serializers.ValidationError("El costo en USD debe ser mayor a 0.")
        return value