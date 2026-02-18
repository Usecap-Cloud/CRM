try:
    with open('initial_data.json', 'r', encoding='utf-8') as f:
        f.read()
    print("UTF-8 OK")
except UnicodeDecodeError as e:
    print(f"UTF-8 Error: {e}")
    try:
        with open('initial_data.json', 'r', encoding='latin-1') as f:
            f.read()
        print("Latin-1 OK")
    except UnicodeDecodeError as e2:
        print(f"Latin-1 Error: {e2}")
