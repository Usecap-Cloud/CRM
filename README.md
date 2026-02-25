# USECAP CRM

Sistema de Gestión de Clientes y Seguimiento para USECAP Chile.

## Requisitos Previos
- Python 3.10+
- MySQL Server

## Instalación y Configuración

### 1. Preparar Entorno
```powershell
# Clonar y entrar al proyecto
cd crm_usecap

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Variables de Entorno
Crea un archivo `.env` en la raíz basado en `.env.example`:
```powershell
copy .env.example .env
```
Edita el `.env` con tus credenciales de MySQL local.

### 3. Base de Datos y Datos Iniciales
```powershell
# Ejecutar migraciones
python manage.py migrate

# Cargar roles y datos base (IMPORTANTE)
python manage.py seed_data

# Crear superusuario (para acceso total)
python manage.py createsuperuser
```

### 4. Archivos Estáticos
Para que los estilos se vean correctamente en entornos de prueba/producción:
```powershell
python manage.py collectstatic --noinput
```

### 5. Iniciar Servidor
```powershell
python manage.py runserver
```
- **App**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

---

## Comandos de Mantenimiento
- **Normalizar Datos**: `python manage.py normalize_data` (Limpia RUTs y Teléfonos existentes).
- **Limpiar RUTs**: `python manage.py clean_ruts`.

## Estructura de Documentación
- [DOCUMENTACION.md](./DOCUMENTACION.md): Manual técnico de arquitectura, roles y lógica de negocio.


