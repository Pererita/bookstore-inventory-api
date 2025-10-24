from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Book
from decimal import Decimal
from unittest.mock import patch
import requests

class BookViewSetTestCase(APITestCase):
    """
    Tests para el BookViewSet.
    """
    def setUp(self):
        """
        Configura datos de prueba.
        """
        self.book1 = Book.objects.create(
            title="The Lord of the Rings",
            author="J.R.R. Tolkien",
            isbn="978-0618640157",
            cost_usd=Decimal("20.00"),
            stock_quantity=10,
            category="Fantasy",
            supplier_country="US"
        )
        self.book2 = Book.objects.create(
            title="The Hitchhiker's Guide to the Galaxy",
            author="Douglas Adams",
            isbn="978-0345391803",
            cost_usd=Decimal("15.50"),
            stock_quantity=5,
            category="Sci-Fi",
            supplier_country="GB"
        )
        self.book3 = Book.objects.create(
            title="Foundation",
            author="Isaac Asimov",
            isbn="978-0553803716",
            cost_usd=Decimal("12.00"),
            stock_quantity=20,
            category="Sci-Fi",
            supplier_country="US"
        )

    def test_list_books(self):
        """
        Prueba que se puedan listar los libros.
        """
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_books_by_category(self):
        """
        Prueba el filtro por categoría.
        """
        url = reverse('book-list') + '?category=Sci-Fi'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Verifica que los libros sean de la categoría correcta
        self.assertTrue(all(item['category'] == 'Sci-Fi' for item in response.data))

    def test_filter_books_by_low_stock(self):
        """
        Prueba el filtro por umbral de stock bajo.
        """
        url = reverse('book-list') + '?threshold=10'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Verifica que los libros tengan un stock menor o igual a 10
        self.assertTrue(all(item['stock_quantity'] <= 10 for item in response.data))

    def test_retrieve_book(self):
        """
        Prueba que se pueda obtener un único libro.
        """
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)

    def test_create_book(self):
        """
        Prueba la creación de un nuevo libro.
        """
        url = reverse('book-list')
        data = {
            "title": "Dune",
            "author": "Frank Herbert",
            "isbn": "978-0441013593",
            "cost_usd": "25.00",
            "stock_quantity": 15,
            "category": "Sci-Fi",
            "supplier_country": "US"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 4)
        self.assertEqual(Book.objects.get(isbn="978-0441013593").title, "Dune")

    def test_create_book_invalid_data(self):
        """
        Prueba que la creación falle con datos inválidos (e.g., ISBN duplicado).
        """
        url = reverse('book-list')
        data = {
            "title": "Another Book",
            "author": "Some Author",
            "isbn": self.book1.isbn,  # ISBN duplicado
            "cost_usd": "10.00",
            "stock_quantity": 5,
            "category": "Fiction",
            "supplier_country": "CA"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_book(self):
        """
        Prueba la actualización completa de un libro.
        """
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        data = {
            "title": "The Lord of the Rings (Updated)",
            "author": self.book1.author,
            "isbn": self.book1.isbn,
            "cost_usd": "22.50",
            "stock_quantity": 12,
            "category": "High Fantasy",
            "supplier_country": "UK"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "The Lord of the Rings (Updated)")
        self.assertEqual(self.book1.category, "High Fantasy")

    def test_partial_update_book(self):
        """
        Prueba la actualización parcial de un libro.
        """
        url = reverse('book-detail', kwargs={'pk': self.book2.pk})
        data = {"stock_quantity": 3}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book2.refresh_from_db()
        self.assertEqual(self.book2.stock_quantity, 3)

    def test_delete_book(self):
        """
        Prueba la eliminación de un libro.
        """
        url = reverse('book-detail', kwargs={'pk': self.book3.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 2)
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(pk=self.book3.pk)

    @patch('inventory.views.requests.get')
    @patch('django.conf.settings.LOCAL_CURRENCY', 'CLP')
    @patch('django.conf.settings.PROFIT_MARGIN', Decimal('0.3'))
    def test_calculate_price_success(self, mock_get):
        """
        Prueba el cálculo de precio exitoso.
        """
        # Configurar el mock para simular la respuesta de la API de cambio
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"CLP": "930.50"}}
        
        url = reverse('book-calculate-price', kwargs={'pk': self.book1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()

        expected_selling_price = (self.book1.cost_usd * Decimal("930.50")) * (1 + Decimal('0.3'))
        self.assertAlmostEqual(self.book1.selling_price_local, expected_selling_price, places=2)
        self.assertEqual(response.data['currency'], 'CLP')

    @patch('inventory.views.requests.get')
    def test_calculate_price_api_failure(self, mock_get):
        """
        Prueba el manejo de errores cuando la API de cambio falla.
        """
        mock_get.side_effect = requests.RequestException("API connection failed")
        
        url = reverse('book-calculate-price', kwargs={'pk': self.book1.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("servicio de tasas de cambio no está disponible", response.data['error'])

    @patch('inventory.views.requests.get')
    @patch('django.conf.settings.LOCAL_CURRENCY', 'XYZ') # Moneda no existente
    def test_calculate_price_currency_not_found(self, mock_get):
        """
        Prueba el caso donde la moneda local no se encuentra en la respuesta de la API.
        """
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"USD": "1.0", "EUR": "0.9"}} # No incluye XYZ
        
        url = reverse('book-calculate-price', kwargs={'pk': self.book1.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("es soportada por el servicio de cambio", response.data['error'])