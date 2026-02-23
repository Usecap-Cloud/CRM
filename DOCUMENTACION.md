# Documentación Técnica

Este documento detalla el funcionamiento, la arquitectura y las reglas de negocio implementadas en el CRM de USECAP.

---

## 1. Arquitectura General
*   **Backend**: Django 4.2+ (Python)
*   **Base de Datos**: MySQL (compatible con entornos locales y Zeabur)
*   **Frontend**: Plantillas de Django con CSS Vanilla (Diseño Premium Dark Mode)
*   **Seguridad**: Autenticación basada en Roles mediante el modelo `Rol` vinculado a cada usuario

### Jerarquía de Roles y Permisos:

#### 1. Administrador / Gerencia (Acceso Total)
*   **Gestión Administrativa**: Control total sobre todos los módulos del sistema.
*   **Estadísticas**: Acceso exclusivo al Dashboard de métricas y gráficos de rendimiento.
*   **Auditoría**: Único rol con permiso para ver el `Audit Log` (historial de cambios de todos los usuarios).
*   **Importación**: Autorizado para realizar cargas masivas de datos vía Excel (`Importación Universal`).
*   **Sincronización**: Acceso a herramientas de mantenimiento técnico (Sync de datos).

#### 2. Vendedor / Ejecutivo Comercial (Acceso Operativo)
*   **Gestión de Cartera**: Puede crear, editar y visualizar Clientes, Encargados, Contratos y Seguimientos.
*   **Módulos de Apoyo**: Acceso a los catálogos de Cursos, Servicios y Proveedores.
*   **Restricciones**:
    *   **NO** puede visualizar el Dashboard de estadísticas globales.
    *   **NO** tiene acceso al historial de auditoría del sistema.
    *   **NO** está autorizado para realizar importaciones masivas (protección de integridad de datos).

---

## 2. Sistema de Normalización de Datos (Data Integrity)
El sistema cuenta con un motor de normalización automática en el archivo `models.py` que garantiza que la base de datos esté siempre limpia.

### A. Gestión de RUTs
*   **Validación**: Algoritmo de Módulo 11 (Chile). No permite guardar RUTs inválidos o sin dígito verificador.
*   **Normalización**: Transforma cualquier entrada a formato estándar `12.345.678-9`.

### B. Gestión Telefónica
*   **Validación**: Exige exactamente **9 dígitos** (estándar nacional).
*   **Normalización**: Formatea automáticamente a **`+56 9 XXXX XXXX`**.

### C. Textos y Abreviaciones
*   **Smart Title Case**: Convierte nombres y razones sociales a Capital Case (ej: de "JUAN PEREZ" a "Juan Perez").
*   **Preservación de Siglas**: Lista blanca de términos que permanecen en mayúsculas: `OTEC`, `SENCE`, `SPA`, `LTDA`, `RRHH`, `TI`, `RM`.

---

## 3. Módulos Principales

### Clientes y Encargados
*   Vínculo automático entre Empresa (Cliente) y sus contactos (Encargados).
*   **Jerarquía de Empresas**: Soporte para **Casa Matriz y Filiales** mediante el campo `cliente_padre`.
*   Cálculo automático de estado por convenio.

### Ejecutivos
*   Gestión de equipos comerciales vinculada a usuarios de Django.
*   Campos específicos: `departamento` y `especialidad`.

### Contratos y Propuestas
*   **Diferenciación Visual**: Los contratos se marcan en **Verde**, las propuestas en **Azul**.
*   Gestión de estados: Pendiente, Firmado, Por Cerrar, etc.

### Importación Masiva (Excel)
*   Motor de carga universal que soporta todos los módulos.
*   **Lógica de Mapeo**: Permite cargar datos aunque las columnas del Excel no tengan el nombre exacto del sistema.
*   **Validación Preventiva**: Antes de cargar, valida que no existan duplicados y que los RUTs sean correctos.

---

## 4. Guía de Interfaz (UI/UX)
El sistema utiliza un código de colores semántico para facilitar la navegación rápida:

*   🟢 **Éxito / Activo**: Usado para estados "Activo", "Firmado" y Registros tipo "Contrato".
*   🔵 **Información / Edición**: Usado para estados "En Proceso" y Registros tipo "Propuesta".
*   🟠 **Advertencia**: Usado para estados "Pendiente" o "Por Cerrar".
*   🔴 **Peligro / Inactivo**: Usado para eliminar registros o estados "Inactivos".

---

## 5. Funcionalidades de Usuario (UX)

### Buscador en Tiempo Real
Todos los módulos de tabla incluyen una barra de búsqueda de alto rendimiento:
*   **Filtro Global**: Utiliza la función `filterTable` (en `base.html`) para proporcionar un comportamiento de búsqueda consistente en todos los módulos (Servicios, Clientes, Ejecutivos, Encargados, Contratos, Cursos y Proveedores).
*   **Feedback Instantáneo**: La tabla se filtra automáticamente mientras el usuario escribe, permitiendo encontrar datos por cualquier campo (RUT, Nombre, Email, Estado, etc.).

### Sistema de Alertas Proactivo
La barra lateral (sidebar) incluye un sistema de notificaciones inteligentes:
*   **Badge de Seguimiento**: Un punto de notificación dinámico (badge rojo) aparece junto al enlace de "Seguimiento".
*   **Lógica por Rol**: El sistema detecta automáticamente los seguimientos pendientes (sin cerrar). Si el usuario es **Administrador**, verá el total global; si es **Ejecutivo**, verá solo sus alertas personales de su propia cartera.
*   **Auto-Actualización**: La función `updateAlertBadges` verifica periódicamente los pendientes y actualiza la interfaz sin necesidad de recargar la página.

### Agenda Inteligente y Vencimientos
El sistema gestiona la criticidad del tiempo mediante:
*   **Código de Colores de Urgencia**: En el calendario de seguimientos, las actividades se marcan con:
    *   🔴 **Rojo**: Gestiones **vencidas** (atrasadas).
    *   🟡 **Naranja/Amarillo**: Gestiones para **hoy o mañana**.
    *   🔵 **Azul**: Gestiones programadas para el **futuro**.
    *   ⚫ **Gris oscuro**: Gestiones ya completadas (**cerradas**).
*   **Dashboard Priorizado**: La sección de "Agenda" en el inicio ordena automáticamente los contratos próximos a vencer, permitiendo una gestión proactiva de renovaciones.
*   **Centro de Seguimiento (Calendario)**: Integra `FullCalendar` para visualizar hitos temporales. Las "Acciones Próximas" se programan basándose en la `Fecha Seguimiento`, apareciendo automáticamente en el calendario del ejecutivo.
*   **Panel de Alertas Próximas**: Filtra y destaca automáticamente todas las gestiones que deben realizarse en los próximos **7 días**, garantizando que ningún compromiso con el cliente se olvide.
*   **Trazabilidad de Fechas**: Cada seguimiento permite registrar hasta 4 hitos temporales (`Fecha Envío`, `Fecha Respuesta`, `Fecha Seguimiento` y `Fecha Respuesta Seguimiento`) para un control total sobre los tiempos de respuesta.
*   **Control de Vigencia**: Los indicadores del Dashboard filtran automáticamente contratos terminados, enfocando la atención del usuario solo en lo que está vigente o por expirar y en cierres urgentes ("Por Cerrar").

---

## 6. Gestión de Usuarios y Ejecutivos

### Creación Automática de Accesos
Al importar ejecutivos masivamente o crearlos en el sistema, se genera automáticamente un **Usuario de Sistema** vinculado:
*   **Username**: Se deriva del email (parte anterior al @).
*   **Contraseña Provisional**: Se genera siguiendo el patrón `USECAP_[RUT_SIN_PUNTOS]`. Ejemplo: Para el RUT 12.345.678-5, la clave sería `USECAP_12345678`.

### Asignación de Cartera (Vendedores)
La asignación de ejecutivos comerciales a la data se realiza en tres niveles:
1.  **Ficha de Cliente**: Cada empresa tiene un Ejecutivo asignado que es el dueño de la cuenta (el "Vendedor").
2.  **Encargados**: Los contactos del cliente heredan el ejecutivo asignado a la empresa, pero pueden ser reasignados individualmente si un ejecutivo distinto gestiona a esa persona.
3.  **Contratos y Seguimientos**: Cada contrato y cada acción de seguimiento quedan vinculados al Ejecutivo que los crea, asegurando que cada vendedor gestione solo su propia agenda (a menos que sea Administrador).

---

## 7. Métrica y Lógica Comercial

### Seguimientos y Cierre de Tareas
Cada registro de **Seguimiento** tiene un propósito operativo:
*   **Estado Abierto**: La gestión está en curso. El sistema la cuenta como "Pendiente" y activa las alertas visuales en el calendario.
*   **Flag Cerrado**: Al marcar una gestión como `Cerrado`, el círculo de seguimiento se completa. El registro se vuelve **Gris** en el calendario y deja de sumar al contador de alertas del Sidebar. Es la señal para el vendedor de que esa tarea específica se finalizó.

### Indicadores Financieros
Aunque el CRM es principalmente operativo, permite capturar data financiera crítica por cada contrato:
*   **Costos Negociados**: Se registran los valores acordados con proveedores para cada servicio.
*   **Precios Unitarios**: Seguimiento de los valores de venta por curso o servicio.
*   **Totales**: El Dashboard resume el volumen total de contratos para análisis administrativo.

---

## 8. Auditoría y Registro
*   **Audit Log**: El sistema registra automáticamente quién creó, editó o eliminó cualquier registro, incluyendo la fecha y el objeto afectado.

---

## 8. Comandos de Administración útiles
*   `python manage.py makemigrations api`: Crear cambios en la base de datos.
*   `python manage.py migrate api`: Aplicar cambios.
*   `python manage.py seed_data`: Cargar base de datos inicial.

---

**Desarrollado para:** USECAP Chile  
**Última Actualización:** Febrero 2026
