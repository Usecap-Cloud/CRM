path = r"C:\Users\arand\OneDrive\Desktop\Workloads (6)\Workloads\Workloads\crm_usecap\backend\templates\base.html"
with open(path, 'rb') as f:
    content = f.read()

target = b"{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or\r\n            request.user.ejecutivo.rol.nombre == 'Gerencia' %}"
replacement = b"{% if request.user.is_superuser or request.user.ejecutivo.rol.nombre == 'Administrador' or request.user.ejecutivo.rol.nombre == 'Gerencia' %}"

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'wb') as f:
        f.write(new_content)
    print("FIX_SUCCESS")
else:
    print("TARGET_NOT_FOUND")
    # Try with \n just in case
    target_lf = target.replace(b'\r\n', b'\n')
    if target_lf in content:
        print("FOUND_LF_INSTEAD")
