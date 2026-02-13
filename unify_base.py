import os

path = r"C:\Users\arand\OneDrive\Desktop\Workloads (6)\Workloads\Workloads\crm_usecap\backend\templates\base.html"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i in range(len(lines)):
    if skip_next:
        skip_next = False
        continue
        
    line = lines[i]
    # Detectar el patrón dividido
    if "{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or" in line:
        if i + 1 < len(lines) and "request.user.ejecutivo.rol.nombre == 'Gerencia' %}" in lines[i+1]:
            # Unificar en una sola línea manteniendo la indentación
            indent = line[:line.find('{%')]
            unified = indent + "{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or request.user.ejecutivo.rol.nombre == 'Gerencia' %}\n"
            new_lines.append(unified)
            skip_next = True
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.writelines(new_lines)

print("UNIFICATION_SUCCESSFUL")
