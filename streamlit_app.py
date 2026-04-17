import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# Setup
st.set_page_config(page_title="Order Dashboard")
st.title("⚓ Mein Schicht-Dashboard")

# API Key
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🔑 API Key fehlt!")

def parse_sms(sms_text):
    # Einfachster Aufruf ohne Zusatzoptionen
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Extrahiere Daten aus dieser SMS: '{sms_text}'
    Antworte NUR mit JSON im Format:
    {{"typ": "Order", "datum": "2026-04-10", "schicht": "1", "ort": "Ort", "zeit": "6:00-14:00", "rolle": "Beruf"}}
    """
    
    response = model.generate_content(prompt)
    
    # Text säubern falls Gemini ```json dazuschreibt
    clean_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(clean_text)

# Sitzungsspeicher
if 'orders' not in st.session_state:
    st.session_state.orders = []

# Interface
sms_input = st.text_area("SMS Text hier einfügen:")
if st.button("Analysieren"):
    try:
        result = parse_sms(sms_input)
        st.session_state.orders.append(result)
        st.success("Erfolgreich!")
    except Exception as e:
        st.error(f"Fehler: {e}")

# Tabelle
if st.session_state.orders:
    st.table(pd.DataFrame(st.session_state.orders))
