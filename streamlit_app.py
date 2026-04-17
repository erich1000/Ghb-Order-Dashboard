import streamlit as st
import pandas as pd
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import json

# Dashboard Setup
st.set_page_config(page_title="Order Dashboard", layout="wide")
st.title("⚓ Mein Schicht-Dashboard")

# API Verbindung mit Versions-Erzwingung
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🔑 API Key fehlt!")

def parse_sms(sms_text):
    # Hier erzwingen wir die API-Version v1 (statt v1beta)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Analysiere diese SMS: '{sms_text}'
    Extrahiere die Infos als JSON.
    Format: {{"typ": "Order", "datum": "YYYY-MM-DD", "schicht": "1", "ort": "Ort", "zeit": "6:00-14:00", "rolle": "Beruf"}}
    """
    
    # Der entscheidende Fix: request_options erzwingt die stabile Version
    response = model.generate_content(
        prompt, 
        request_options=RequestOptions(api_version='v1')
    )
    
    clean_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(clean_text)

# Speicher & Interface
if 'orders' not in st.session_state:
    st.session_state.orders = []

sms_input = st.text_area("SMS Text hier einfügen:")
if st.button("Analysieren"):
    try:
        with st.spinner('Gemini analysiert...'):
            daten = parse_sms(sms_input)
            st.session_state.orders.append(daten)
            st.success("Erfolgreich!")
    except Exception as e:
        st.error(f"Fehler: {e}")

if st.session_state.orders:
    st.subheader("Deine Schicht-Historie")
    st.table(pd.DataFrame(st.session_state.orders))
