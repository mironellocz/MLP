import streamlit as st
import requests

# 1. Nastavení stránky
st.set_page_config(page_title="Mironovo hledání v MLP", page_icon="📚")

# --- FUNKCE PRO VYHLEDÁVÁNÍ ---
@st.cache_data(ttl=3600)
def ziskej_data_z_knihovny(titul, jen_dostupne):
    url = "https://www.knihovny.cz/api/v1/search"
    
    # Základní filtry
    # 'building:MLP' omezí hledání pouze na Městskou knihovnu v Praze
    filtry = ["building:MLP"]
    
    # Pokud uživatel zaškrtne 'jen dostupné', přidáme filtr statusu
    if jen_dostupne:
        filtry.append("status:available")
    
    params = {
        "lookfor": titul,
        "type": "Title",
        "sort": "relevance",
        "limit": 20,
        "filter[]": filtry
    }
    
    headers = {
        "User-Agent": "KnihovniHledacMLP/1.0 (kontakt: vase@email.cz)"
    }
    
    response = requests.get(url, params=params, headers=headers)
    return response

# --- WEBOVÉ ROZHRANÍ ---
st.title("📚 Vyhledávač Městské knihovny v Praze")
st.info("Vyhledáváte pouze ve fondu Městské knihovny v Praze (přes rozhraní Knihovny.cz).")

# Nastavení v postranním panelu
with st.sidebar:
    st.header("Nastavení")
    jen_dostupne = st.checkbox("Pouze dostupné k vypůjčení", value=False)
    st.write("---")
    st.caption("Data jsou čerpána z portálu Knihovny.cz")

hledany_titul = st.text_input("Zadejte název knihy:", placeholder="Např. Saturnin")

if st.button("Vyhledat"):
    if hledany_titul:
        with st.spinner('Prohledávám fond MLP...'):
            try:
                response = ziskej_data_z_knihovny(hledany_titul, jen_dostupne)
                
                if response.status_code == 200:
                    data = response.json()
                    pocet = data.get("resultCount", 0)
                    
                    if pocet > 0:
                        st.success(f"Nalezeno {pocet} titulů v MLP.")
                        
                        for record in data.get("records", []):
                            # Vytvoření přehledné karty pro každou knihu
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.subheader(record.get("title"))
                                    autori = record.get("authors", {}).get("primary", {})
                                    autor = ", ".join(autori.keys()) if autori else "Neznámý autor"
                                    st.write(f"👤 **Autor:** {autor}")
                                    st.write(f"📅 **Rok:** {record.get('publicationDates', ['-'])[0]}")
                                
                                with col2:
                                    id_knihy = record.get("id")
                                    st.link_button("Detail / Rezervovat", f"https://www.knihovny.cz/Record/{id_knihy}")
                                st.write("---")
                    else:
                        st.warning("V Městské knihovně v Praze nebylo nic nalezeno. Zkuste jiný název nebo vypněte filtr dostupnosti.")
                
                elif response.status_code == 429:
                    st.error("Příliš mnoho dotazů (Chyba 429). Počkejte prosím chvíli.")
                else:
                    st.error(f"Chyba serveru: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Došlo k chybě: {e}")
    else:
        st.info("Napište název knihy, kterou hledáte.")
