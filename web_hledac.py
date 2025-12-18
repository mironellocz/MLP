import streamlit as st
import requests
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(
    page_title="Hledání v MLP", 
    page_icon="📚", 
    layout="centered"
)

# --- LOGIKA VYHLEDÁVÁNÍ ---
@st.cache_data(ttl=1800, show_spinner=False)
def hledej_v_knihovne(titul, jen_dostupne):
    # Používáme stabilnější API endpoint MZK, který obsluhuje Knihovny.cz
    url = "https://vufind.mzk.cz/api/v1/search"
    
    # Parametry pro Městskou knihovnu v Praze (MLP)
    filtry = ["building:MLP"]
    if jen_dostupne:
        filtry.append("status:available")
    
    params = {
        "lookfor": titul,
        "type": "Title",
        "sort": "relevance",
        "limit": 20,
        "filter[]": filtry
    }
    
    # Simulace moderního prohlížeče pro obejití firewallů
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        # Timeout nastaven na 15 sekund pro pomalejší odezvy serveru
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            return "chyba_429"
        else:
            return f"chyba_serveru_{response.status_code}"
            
    except requests.exceptions.Timeout:
        return "chyba_timeout"
    except requests.exceptions.ConnectionError:
        return "chyba_pripojeni"
    except Exception as e:
        return f"chyba_obecna_{str(e)[:30]}"

# --- WEBOVÉ ROZHRANÍ (UI) ---
st.title("🔍 Vyhledávač v fondu MLP")
st.markdown("Hledáte knihy přímo v **Městské knihovně v Praze**.")

# Boční panel s nastavením
with st.sidebar:
    st.header("⚙️ Nastavení")
    pouze_volne = st.checkbox("Pouze dostupné tituly", value=True, help="Zobrazí jen knihy, které nejsou momentálně vypůjčené.")
    st.divider()
    st.caption("Aplikace využívá API rozhraní Knihovny.cz")

# Hlavní vstup
dotaz = st.text_input("Název knihy nebo jméno autora:", placeholder="Např. Saturnin nebo Jirotka")

if st.button("🚀 Spustit hledání", use_container_width=True):
    if dotaz:
        with st.status("Propojuji se s databází...", expanded=True) as status:
            vysledek = hledej_v_knihovne(dotaz, pouze_volne)
            
            if isinstance(vysledek, dict):
                status.update(label="Hledání dokončeno!", state="complete", expanded=False)
                pocet = vysledek.get("resultCount", 0)
                
                if pocet > 0:
                    st.success(f"Nalezeno {pocet} záznamů v Městské knihovně")
                    
                    for record in vysledek.get("records", []):
                        with st.container(border=True):
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                st.subheader(record.get("title", "Bez názvu"))
                                
                                # Zpracování autorů
                                autori_data = record.get("authors", {}).get("primary", {})
                                autor = ", ".join(autori_data.keys()) if autori_data else "Autor neuveden"
                                st.write(f"👤 **Autor:** {autor}")
                                
                                # Rok vydání
                                roky = record.get("publicationDates", ["-"])
                                st.write(f"📅 **Rok:** {roky[0]}")
                            
                            with c2:
                                id_knihy = record.get("id")
                                link = f"https://www.knihovny.cz/Record/{id_knihy}"
                                st.link_button("Katalog ↗️", link)
                else:
                    st.warning("V MLP nebyl nalezen žádný titul odpovídající zadání.")
            
            # Zpracování chybových stavů
            elif vysledek == "chyba_429":
                status.update(label="Chyba: Přetížení", state="error")
                st.error("⚠️ Server je přetížen. Zkuste to prosím znovu za minutu.")
            elif vysledek == "chyba_pripojeni":
                status.update(label="Chyba připojení", state="error")
                st.error("❌ Nepodařilo se navázat spojení se serverem knihovny. Streamlit Cloud může být dočasně blokován.")
                st.info("Tip: Zkuste aplikaci spustit lokálně na svém PC, tam pravděpodobně poběží bez problémů.")
            elif vysledek == "chyba_timeout":
                status.update(label="Čas vypršel", state="error")
                st.error("⌛ Server knihovny neodpovídá včas. Zkuste to za chvíli.")
            else:
                status.update(label="Neznámá chyba", state="error")
                st.error(f"Omlouváme se, došlo k problému: {vysledek}")
    else:
        st.info("Zadejte prosím hledaný výraz do pole výše.")
