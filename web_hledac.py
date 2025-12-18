import streamlit as st
import requests

# Nastavení stránky
st.set_page_config(page_title="Hledání v knihovnách", page_icon="📚")

# --- FUNKCE PRO VYHLEDÁVÁNÍ S CACHE ---
# Cache zajistí, že se stejný dotaz neposílá na server znovu a znovu
@st.cache_data(ttl=3600)  # Výsledky se pamatují 1 hodinu
def ziskej_data_z_knihovny(titul):
    url = "https://www.knihovny.cz/api/v1/search"
    params = {
        "lookfor": titul,
        "type": "Title",
        "sort": "relevance",
        "limit": 10
    }
    headers = {
        "User-Agent": "MojeKnihovniAplikace/1.0 (kontakt: muj-email@seznam.cz)"
    }
    
    response = requests.get(url, params=params, headers=headers)
    return response

# --- WEBOVÉ ROZHRANÍ ---
st.title("📚 Vyhledávač v Knihovny.cz")
hledany_titul = st.text_input("Název titulu nebo autor:", placeholder="Např. Saturnin")

if st.button("Vyhledat"):
    if hledany_titul:
        with st.spinner('Hledám v databázi...'):
            try:
                response = ziskej_data_z_knihovny(hledany_titul)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("resultCount", 0) > 0:
                        st.success(f"Nalezeno {data['resultCount']} výsledků.")
                        for record in data.get("records", []):
                            with st.expander(f"📖 {record.get('title')}"):
                                autori = record.get("authors", {}).get("primary", {})
                                autor = ", ".join(autori.keys()) if autori else "Neznámý autor"
                                st.write(f"**Autor:** {autor}")
                                st.write(f"**Rok:** {record.get('publicationDates', ['-'])[0]}")
                                st.markdown(f"[Zobrazit detail](https://www.knihovny.cz/Record/{record.get('id')})")
                    else:
                        st.warning("Nebylo nic nalezeno.")
                
                elif response.status_code == 429:
                    st.error("Chyba 429: Server je přetížen. Zkuste to prosím za minutu. Server nás dočasně omezil kvůli příliš mnoha dotazům.")
                else:
                    st.error(f"Chyba serveru: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Došlo k chybě: {e}")
