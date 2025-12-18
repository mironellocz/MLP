import streamlit as st
import requests
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Hledání v MLP", page_icon="📚", layout="centered")

# --- GRAFICKÉ ROZHRANÍ (UI) ---
st.title("🔍 Hledač v Městské knihovně")
st.markdown("Prohledává fond **Městské knihovny v Praze** přes rozhraní Knihovny.cz.")

# Sidebar pro nastavení
with st.sidebar:
    st.header("⚙️ Filtry")
    pouze_volne = st.checkbox("Pouze dostupné k vypůjčení", value=False)
    st.divider()
    st.caption("Verze 2.1 | Ochrana proti chybě 429 aktivní")

# Hlavní vyhledávací pole
dotaz = st.text_input("Zadejte název knihy nebo autora:", placeholder="Např. Malý princ")

if st.button("🔎 Vyhledat tituly", use_container_width=True):
    if dotaz:
        with st.spinner('Komunikuji se serverem knihovny...'):
            vysledek = hledej_v_knihovne(dotaz, pouze_volne)
            
            if vysledek == "error_429":
                st.error("⚠️ Server Knihovny.cz je momentálně přetížen (chyba 429). Zkuste to prosím znovu za 1-2 minuty.")
            elif isinstance(vysledek, str) and vysledek.startswith("error"):
                st.error(f"❌ Došlo k chybě při spojení se serverem ({vysledek}).")
            else:
                pocet = vysledek.get("resultCount", 0)
                
                if pocet > 0:
                    st.success(f"Nalezeno {pocet} výsledků v MLP")
                    
                    for record in vysledek.get("records", []):
                        with st.container(border=True):
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.subheader(record.get("title", "Neznámý název"))
                                autori = record.get("authors", {}).get("primary", {})
                                autor = ", ".join(autori.keys()) if autori else "Neznámý autor"
                                st.write(f"👤 **Autor:** {autor}")
                                st.write(f"📅 **Rok vydání:** {record.get('publicationDates', ['-'])[0]}")
                            
                            with col2:
                                id_knihy = record.get("id")
                                link = f"https://www.knihovny.cz/Record/{id_knihy}"
                                st.link_button("Detail", link)
                else:
                    st.warning("V MLP nebyl nalezen žádný odpovídající titul.")
    else:
        st.info("Zadejte název knihy.")

