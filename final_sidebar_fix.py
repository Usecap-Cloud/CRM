import re

path = r"C:\Users\arand\OneDrive\Desktop\Workloads (6)\Workloads\Workloads\crm_usecap\backend\templates\base.html"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Corregir sintaxis multilínea
pattern_if = r"\{% if request\.user\.is_superuser or request\.user\.ejecutivo\.rol\.nombre == 'Administrador' or\s+request\.user\.ejecutivo\.rol\.nombre == 'Gerencia' %\}"
replacement_if = "{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or request.user.ejecutivo.rol.nombre == 'Gerencia' %}"
content = re.sub(pattern_if, replacement_if, content)

# 2. Corregir Iconos
# Inicio: Laptop -> Casa con jardín
content = content.replace('&#x1F4BB;</span> Inicio', '&#x1F3E1;</span> Inicio')
# Cursos: Libro -> Libros de colores
content = content.replace('&#x1F4D6;</span> Cursos', '&#x1F4DA;</span> Cursos')
# Servicios: Herramientas -> Libro abierto
content = content.replace('&#x1F6E0;</span> Servicios', '&#x1F4D6;</span> Servicios')
# Contratos: Asegurarnos que sea la libreta (ya debería estar)
content = content.replace('&#x1F4DC;</span> Contratos', '&#x1F4DD;</span> Contratos') # Por si acaso estaba el pergamino

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print("FIX_COMPLETED_SUCCESSFULLY")
