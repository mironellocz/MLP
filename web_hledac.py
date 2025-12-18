import streamlit as st
import requests

# Nastavení vzhledu stránky
st.set_page_config(page_title="Hledání v knihovnách", page_icon="📚")

st.title("📚 Vyhledávač v Knihovny.cz")
st.write("Zadejte název knihy a já ji najdu v českých knihovnách.")

# Vstupní pole
hledany_titul = st.text_input("Název titulu nebo autor:", placeholder="Např. Babička")

if st.button("Vyhledat"):
    if hledany_titul:
        url = "https://www.knihovny.cz/api/v1/search"
        params = {
            "lookfor": hledany_titul,
            "type": "Title",
            "sort": "relevance",
            "limit": 10
        }
        
        with st.spinner('Hledám v databázi...'):
            try:
                response = requests.get(url, params=params)
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
                            # Odkaz přímo na portál
                            id_knihy = record.get("id")
                            st.markdown(f"[Zobrazit detail na Knihovny.cz](https://www.knihovny.cz/Record/{id_knihy})")
                else:
                    st.warning("Nebylo nic nalezeno.")
            except Exception as e:
                st.error(f"Došlo k chybě: {e}")
    else:
        st.info("Zadejte prosím název knihy.")