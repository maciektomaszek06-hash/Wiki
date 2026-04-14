import streamlit as st
import re
import requests

# Konfiguracja strony
st.set_page_config(page_title="Wiki Link Bot", page_icon="🤖")

HEADERS = {
    'User-Agent': 'LinkInterwikiBot/3.0 (kontakt: twoj@email.com)'
}

def get_best_qid(title):
    title_clean = title.strip()
    wiki_url = "https://pl.wikipedia.org/w/api.php"
    params = {"action": "query", "titles": title_clean, "prop": "pageprops", "redirects": 1, "format": "json"}
    
    try:
        res = requests.get(wiki_url, params=params, headers=HEADERS).json()
        pages = res.get('query', {}).get('pages', {})
        if pages and int(list(pages.keys())[0]) > 0:
            return None, True
            
        wd_url = "https://www.wikidata.org/w/api.php"
        wd_params = {"action": "wbsearchentities", "search": title_clean, "language": "pl", "format": "json", "limit": 5}
        wd_res = requests.get(wd_url, params=wd_params, headers=HEADERS).json()
        
        results = wd_res.get('search', [])
        if not results: return None, False
        return results[0]['id'], False
    except:
        return None, False

def process_wikicode(text):
    link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    matches = list(link_pattern.finditer(text))
    for match in reversed(matches):
        target = match.group(1).strip()
        label = match.group(2).strip() if match.group(2) else target
        qid, exists_pl = get_best_qid(target)
        
        if not exists_pl and qid:
            replacement = f"{{{{link-interwiki|{target}|Q={qid}|tekst={label}}}}}"
            text = text[:match.start()] + replacement + text[match.end():]
    return text

# Interfejs Streamlit
st.title("🤖 Wiki Link Interwiki Bot")
st.write("Wklej tekst z wikikodem, a ja zamienię brakujące linki na szablon link-interwiki.")

user_input = st.text_area("Tekst wejściowy:", height=300, placeholder="Wpisz np. [[Albert Einstein]]...")

if st.button("Przetwórz tekst"):
    if user_input:
        with st.spinner('Przeszukuję Wikipedię i Wikidane...'):
            result = process_wikicode(user_input)
            st.subheader("Wynik:")
            st.code(result, language="markdown")
            st.success("Gotowe!")
    else:
        st.warning("Proszę wpisać jakiś tekst.")
