path = r"C:\Users\arand\OneDrive\Desktop\Workloads (6)\Workloads\Workloads\crm_usecap\backend\templates\base.html"
with open(path, 'rb') as f:
    content = f.read()

# Buscamos todas las variaciones posibles de la etiqueta dividida
targets = [
    b"{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or\r\n            request.user.ejecutivo.rol.nombre == 'Gerencia' %}",
    b"{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or\n            request.user.ejecutivo.rol.nombre == 'Gerencia' %}",
    b"{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or\r\n             request.user.ejecutivo.rol.nombre == 'Gerencia' %}"
]

replacement = b"{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or request.user.ejecutivo.rol.nombre == 'Gerencia' %}"

fixed = False
for target in targets:
    if target in content:
        content = content.replace(target, replacement)
        fixed = True

if fixed:
    with open(path, 'wb') as f:
        f.write(content)
    print("FIX_SUCCESS")
else:
    # Intento más agresivo: buscar por partes y unir
    import re
    # Convertimos a string para usar regex pero con cuidado de los finales de línea
    text = content.decode('utf-8', errors='ignore')
    pattern = r"\{% if request\.user\.is_superuser or request\.user\.ejecutivo\.rol\.nombre == 'Administrador' or\s+request\.user\.ejecutivo\.rol\.nombre == 'Gerencia' %\}"
    new_text = re.sub(pattern, replacement.decode('utf-8'), text)
    
    if new_text != text:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new_text)
        print("FIX_SUCCESS_REGEX")
    else:
        print("TARGET_NOT_FOUND")
