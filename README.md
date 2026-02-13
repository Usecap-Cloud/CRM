# USECAP CRM

## Status
- Last Branding Update: 2026-02-13 18:20 (Triggering Deployment)

# Crear entorno virtual con CMD
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env


# Ejecutar migraciones de Django
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# PASO 4: Iniciar Backend
python manage.py runserver

Backend corriendo en: http://localhost:8000  
Admin panel: http://localhost:8000/admin  
API: http://localhost:8000/api/


# PROBAR EL BACKEND

# Opción 1: Panel de Admin Django
1. Ve a: http://localhost:8000/admin
2. Ingresa con tu superusuario
3. Puedes crear/editar todos los registros desde aquí

# Opción 2: API REST (con Postman/Thunder Client)

# Login

POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "tu_password"
}

# Crear Cliente
POST http://localhost:8000/api/clientes/
Authorization: Bearer tu_token_aqui
Content-Type: application/json

{
  "razon_social": "Empresa Demo",
  "rut_empresa": "76123456-7",
  "contacto_principal": "Juan Pérez",
  "email_contacto": "juan@empresa.cl",
  "estado_cliente": "prospecto",
  "ejecutivo_asignado": 1
}

