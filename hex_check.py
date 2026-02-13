with open(r"C:\Users\arand\OneDrive\Desktop\Workloads (6)\Workloads\Workloads\crm_usecap\backend\templates\base.html", 'rb') as f:
    content = f.read()
    idx = content.find(b'if request.user.is_superuser')
    if idx != -1:
        chunk = content[idx:idx+400]
        print("START_CHUNK")
        print(chunk)
        print("END_CHUNK")
    else:
        print("Not found")
