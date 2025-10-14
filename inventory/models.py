from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

class Book(models.Model):
    """
    Modelo para representar un libro en el inventario de la librería.
    """
    isbn_validator = RegexValidator(
        regex=r'^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$',
        message="El ISBN debe ser un número de 10 o 13 dígitos."
    )

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(
        max_length=17,
        unique=True,
        validators=[isbn_validator],
        help_text="ISBN único del libro (10 o 13 dígitos)."
    )
    cost_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Costo del libro en USD, debe ser mayor a 0."
    )
    selling_price_local = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precio de venta en moneda local, puede ser nulo."
    )
    stock_quantity = models.PositiveIntegerField(
        help_text="Cantidad de stock disponible, debe ser un entero no negativo."
    )
    category = models.CharField(max_length=100)
    supplier_country = models.CharField(
        max_length=2,
        help_text="Código de país debe ser de 2 letras (ISO 3166-1 alpha-2)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']