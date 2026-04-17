import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# Seite einrichten
st.set_page_config(page_title="Order Dashboard", layout="wide")

# API Key Konfiguration
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🔑 API Key fehlt!")

def parse_sms_with_gemini(sms_text):
    # Wir nutzen hier die modernste Bezeichnung
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"Analysiere diese SMS: '{sms_text}'. Gib NUR JSON zurück: {{'typ': 'Order', 'datum': 'YYYY-MM-DD', 'schicht': '1', 'ort': 'Ort', 'zeit': '6-00-14-00', 'rolle': 'Beruf'}}"
    
    # Der Aufruf ohne zusätzliche Pfade
    response = model.generate_content(prompt)
    
    # JSON säubern
    output = response.text.strip()
    if output.startswith("```"):
        output = output.split("json")[-1].split("```")[0].strip()
        
    return json.loads(output)

st.title("⚓ Mein Schicht-Dashboard")

if 'orders' not in st.session_state:
    st.session_state.orders = []

with st.expander("Manuelle SMS Eingabe", expanded=True):
    test_sms = st.text_area("SMS Text hier einfügen:")
    if st.button("Analysieren"):
        try:
            with st.spinner('Gemini arbeitet...'):
                result = parse_sms_with_gemini(test_sms)
                st.session_state.orders.append(result)
                st.success("Erfolgreich hinzugefügt!")
        except Exception as e:
            st.error(f"Fehler: {e}")

if st.session_state.orders:
    st.subheader("Deine Schichten")
    st.table(pd.DataFrame(st.session_state.orders))
