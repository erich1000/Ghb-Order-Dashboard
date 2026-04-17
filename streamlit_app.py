import streamlit as st
import pandas as pd
from google import genai
import json

# Dashboard Setup
st.set_page_config(page_title="Order Dashboard", layout="wide")
st.title("⚓ Mein Schicht-Dashboard")

# API Key aus den Secrets laden
if "GOOGLE_API_KEY" in st.secrets:
    # Der neue 2026 Client-Standard
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🔑 API Key fehlt in den Streamlit-Secrets!")
    st.stop()

def parse_sms(sms_text):
    # Aufruf über die neue genai-Struktur
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"Extrahiere JSON aus dieser SMS: '{sms_text}'. Felder: typ, datum, schicht, ort, zeit, rolle."
    )
    
    # Text säubern (entfernt Markdown-Reste)
    clean_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(clean_text)

# Speicher für die Sitzung
if 'orders' not in st.session_state:
    st.session_state.orders = []

# Eingabemaske
with st.container():
    sms_input = st.text_area("SMS Text hier einfügen:", height=150)
    if st.button("🚀 Analysieren"):
        try:
            with st.spinner('Gemini analysiert die Daten...'):
                ergebnis = parse_sms(sms_input)
                st.session_state.orders.append(ergebnis)
                st.success("Erfolgreich hinzugefügt!")
        except Exception as e:
            st.error(f"Technischer Fehler: {e}")

# Anzeige der Tabelle
if st.session_state.orders:
    st.subheader("Deine Schicht-Liste")
    df = pd.DataFrame(st.session_state.orders)
    st.dataframe(df, use_container_width=True)
