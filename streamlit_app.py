import streamlit as st
import pandas as pd
from google import genai
import json

# Setup
st.set_page_config(page_title="Order Dashboard")
st.title("⚓ Mein Schicht-Dashboard")

# API Key Check
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🔑 API Key fehlt in den Secrets!")
    st.stop()

def parse_sms(sms_text):
    # Neuer Aufruf-Standard für 2026
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"Extrahiere JSON aus dieser SMS: '{sms_text}'. Felder: typ, datum, schicht, ort, zeit, rolle."
    )
    
    # Text säubern
    clean_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(clean_text)

# Sitzungsspeicher
if 'orders' not in st.session_state:
    st.session_state.orders = []

# Interface
sms_input = st.text_area("SMS hier einfügen:")
if st.button("Analysieren"):
    try:
        with st.spinner('Gemini analysiert...'):
            daten = parse_sms(sms_input)
            st.session_state.orders.append(daten)
            st.success("Erfolgreich hinzugefügt!")
    except Exception as e:
        st.error(f"Fehler: {e}")

# Tabelle
if st.session_state.orders:
    st.table(pd.DataFrame(st.session_state.orders))
