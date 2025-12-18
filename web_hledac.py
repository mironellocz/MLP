# Přidáme hlavičku User-Agent, aby nás server nepovažoval za bota
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        with st.spinner('Hledám v databázi...'):
            try:
                # Přidáme headers=headers do požadavku
                response = requests.get(url, params=params, headers=headers)
                
                # Kontrola, zda server vůbec odpověděl v pořádku (kód 200)
                if response.status_code != 200:
                    st.error(f"Server knihovny vrátil chybu: {response.status_code}")
                else:
                    data = response.json()
                    # ... zbytek kódu pro vypsání výsledků ...
