import re

path = r"C:\Users\arand\OneDrive\Desktop\Workloads (6)\Workloads\Workloads\crm_usecap\backend\templates\base.html"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Patrón agresivo para encontrar la etiqueta dividida y unificarla
# Buscamos el inicio de la etiqueta hasta el final de la condición en la línea siguiente
pattern = r"\{% if request\.user\.is_superuser or request\.user\.ejecutivo\.rol\.nombre == 'Administrador' or\s+request\.user\.ejecutivo\.rol\.nombre == 'Gerencia' %\}"
replacement = "{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or request.user.ejecutivo.rol.nombre == 'Gerencia' %}"

new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Asegurar el icono de Servicios Ledger
new_content = new_content.replace('&#x1F4D6;</span> Servicios', '&#x1F4D2;</span> Servicios')

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(new_content)

print("FIX_APPLIED")
