import streamlit as st
import requests

# 1. Nastavení vzhledu stránky
st.set_page_config(page_title="Hledání v knihovnách", page_icon="📚")

st.title("📚 Vyhledávač v Knihovny.cz")
st.write("Zadejte název knihy a já ji najdu v českých knihovnách.")

# 2. Vstupní pole
hledany_titul = st.text_input("Název titulu nebo autor:", placeholder="Např. Saturnin")

# 3. Logika vyhledávání po stisknutí tlačítka
if st.button("Vyhledat"):
    if hledany_titul:
        url = "https://www.knihovny.cz/api/v1/search"
        params = {
            "lookfor": hledany_titul,
            "type": "Title",
            "sort": "relevance",
            "limit": 10
        }
        
        # Hlavička User-Agent simuluje prohlížeč a předchází blokování
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        with st.spinner('Hledám v databázi...'):
            try:
                # Odeslání požadavku s parametry a hlavičkou
                response = requests.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("resultCount", 0) > 0:
                        st.success(f"Nalezeno {data['resultCount']} výsledků.")
                        
                        for record in data.get("records", []):
                            with st.expander(f"📖 {record.get('title')}"):
                                autori = record.get("authors", {}).get("primary", {})
                                autor = ", ".join(autori.keys()) if autori else "Neznámý autor"
                                rok = record.get("publicationDates", ["-"])[0]
                                
                                st.write(f"**Autor:** {autor}")
                                st.write(f"**Rok vydání:** {rok}")
                                id_knihy = record.get("id")
                                st.markdown(f"[Zobrazit detail na Knihovny.cz](https://www.knihovny.cz/Record/{id_knihy})")
                    else:
                        st.warning("Nebylo nic nalezeno.")
                else:
                    st.error(f"Chyba serveru: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Došlo k chybě při zpracování dat: {e}")
    else:
        st.info("Zadejte prosím název knihy.")
