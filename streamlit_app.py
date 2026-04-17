import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# Konfiguration
st.set_page_config(page_title="Order Dashboard", layout="wide")

# API Key laden
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Bitte GOOGLE_API_KEY in den Streamlit-Secrets hinterlegen!")

def parse_sms_with_gemini(sms_text):
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    prompt = f"Extrahiere Daten aus dieser SMS: '{sms_text}'. Gib NUR JSON zurück mit den Feldern: typ, datum, schicht, ort, zeit, rolle."
    response = model.generate_content(prompt)
    # Entfernt evtl. Markdown-Formatierung aus der Antwort
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

st.title("⚓ Mein Schicht-Dashboard")

if 'orders' not in st.session_state:
    st.session_state.orders = []

with st.expander("Manuelle SMS Eingabe"):
    test_sms = st.text_area("SMS Text hier einfügen:")
    if st.button("Analysieren"):
        try:
            data = parse_sms_with_gemini(test_sms)
            st.session_state.orders.append(data)
            st.success("Hinzugefügt!")
        except Exception as e:
            st.error(f"Fehler: {e}")

if st.session_state.orders:
    df = pd.DataFrame(st.session_state.orders)
    st.subheader("Aktuelle Schichten")
    st.dataframe(df, use_container_width=True)
