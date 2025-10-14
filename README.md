# Bookstore Inventory API

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django)
![Django REST Framework](https://img.shields.io/badge/DRF-3.14-A30000?style=for-the-badge&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-24-2496ED?style=for-the-badge&logo=docker)

API RESTful para la gestión del inventario de una librería, desarrollada como parte de la prueba técnica para Nextep Innovation. El proyecto está completamente dockerizado para facilitar su configuración y despliegue.

## Características

-   Gestión **CRUD** completa para libros.
-   **Integración externa** con una API de tasas de cambio para calcular precios de venta.
-   Endpoints para **filtrar** libros por categoría y por bajo stock.
-   Manejo de **errores centralizado** para respuestas de API consistentes.
-   Validación de datos a nivel de modelo y serializador.
-   Entorno de desarrollo y producción basado en **Docker y Docker Compose**.

---

## Puesta en Marcha

Sigue estos pasos para levantar el proyecto en tu entorno local.

### **1. Requisitos Previos**

Asegúrate de tener instaladas las siguientes herramientas en tu sistema:

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/) (generalmente incluido con Docker Desktop)

El lenguaje (Python), la base de datos (PostgreSQL) y todas las dependencias del proyecto son gestionadas automáticamente por Docker.

### **2. Configuración del Entorno**

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd bookstore-inventory-api
    ```

2.  **Crea el archivo de variables de entorno:**
    Crea una copia del archivo de ejemplo `.env.example` y renómbrala a `.env`. Este archivo es crucial para configurar la base de datos y la seguridad de Django.
    ```bash
    cp .env.example .env
    ```
    El archivo `.env.example` muestra la estructura necesaria. Para tu entorno local, los valores por defecto funcionarán, pero **es una buena práctica de seguridad generar una nueva `SECRET_KEY`**. Puedes generar una rápidamente con el siguiente comando de Django (ejecutado después de levantar los contenedores):
    ```bash
    docker compose exec web python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    ```
    Copia la clave generada y pégala en tu archivo `.env`.

¡Y listo! La API estará disponible en `http://localhost:8000`.

---

## Documentación de la API (OpenAPI / Swagger)

Este proyecto incluye documentación interactiva autogenerada siguiendo el estándar OpenAPI 3. Esta es la forma recomendada para explorar y probar los endpoints directamente desde el navegador.

Una vez que el proyecto esté en ejecución, puedes acceder a la documentación en la siguiente URL:

**[http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)**

## Uso de la API

A continuación se muestran ejemplos de uso de los endpoints principales utilizando `curl`.

### **Endpoints CRUD Básicos**

#### 1. Crear un Libro

-   **Endpoint**: `POST /api/v1/books/`
-   **Ejemplo**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/books/ \
    -H "Content-Type: application/json" \
    -d '{
          "title": "El Señor de los Anillos",
          "author": "J.R.R. Tolkien",
          "isbn": "978-0618640157",
          "cost_usd": "25.50",
          "stock_quantity": 15,
          "category": "Fantasía",
          "supplier_country": "GB"
        }'
    ```

#### 2. Listar todos los Libros

-   **Endpoint**: `GET /api/v1/books/`
-   **Ejemplo**:
    ```bash
    curl -X GET http://localhost:8000/api/v1/books/
    ```

#### 3. Obtener un Libro por ID

-   **Endpoint**: `GET /api/v1/books/{id}/`
-   **Ejemplo**:
    ```bash
    curl -X GET http://localhost:8000/api/v1/books/1/
    ```

#### 4. Actualizar un Libro

-   **Endpoint**: `PUT /api/v1/books/{id}/`
-   **Ejemplo**:
    ```bash
    curl -X PUT http://localhost:8000/api/v1/books/1/ \
    -H "Content-Type: application/json" \
    -d '{
          "title": "El Señor de los Anillos",
          "author": "J.R.R. Tolkien",
          "isbn": "978-0618640157",
          "cost_usd": "25.50",
          "stock_quantity": 12,
          "category": "Fantasía Épica",
          "supplier_country": "GB"
        }'
    ```

#### 5. Eliminar un Libro

-   **Endpoint**: `DELETE /api/v1/books/{id}/`
-   **Ejemplo**:
    ```bash
    curl -X DELETE http://localhost:8000/api/v1/books/1/
    ```

### **Endpoints Adicionales**

#### 1. Buscar por Categoría

-   **Endpoint**: `GET /api/v1/books/?category={category}`
-   **Ejemplo**:
    ```bash
    curl -X GET "http://localhost:8000/api/v1/books/?category=Fantasía"
    ```

#### 2. Buscar Libros con Stock Bajo

-   **Endpoint**: `GET /api/v1/books/?threshold={value}`
-   **Ejemplo**:
    ```bash
    curl -X GET "http://localhost:8000/api/v1/books/?threshold=10"
    ```

### **Endpoint de Integración Externa**

#### 1. Calcular Precio de Venta

-   **Endpoint**: `POST /api/v1/books/{id}/calculate-price/`
-   **Descripción**: Calcula el precio de venta sugerido basado en el `cost_usd`, una tasa de cambio en tiempo real y un margen de ganancia del 40%. El resultado es guardado en la base de datos.
-   **Ejemplo**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/books/1/calculate-price/
    ```

---

## Comandos Útiles de Docker

-   **Verificar el estado de los contenedores:**
    ```bash
    docker compose ps
    ```
-   **Ver los logs de la aplicación en tiempo real:**
    ```bash
    docker compose logs -f web
    ```
-   **Detener los contenedores:**
    ```bash
    docker compose down
    ```
-   **Acceder a un shell dentro del contenedor de la aplicación:**
    ```bash
    docker compose exec web bash
    ```