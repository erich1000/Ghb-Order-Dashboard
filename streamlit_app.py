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
    # Wir nutzen hier den Standardnamen
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Analysiere diese SMS: '{sms_text}'
    Extrahiere die Infos und antworte NUR mit einem validen JSON-Objekt.
    Format: {{"typ": "Order", "datum": "YYYY-MM-DD", "schicht": "1", "ort": "Ort", "zeit": "HH:mm-HH:mm", "rolle": "Beruf"}}
    """
    
    response = model.generate_content(prompt)
    
    # Sicherstellen, dass wir nur das JSON bekommen, auch wenn Gemini Text drumherum baut
    text_response = response.text
    if "{" in text_response and "}" in text_response:
        start = text_response.find("{")
        end = text_response.rfind("}") + 1
        clean_json = text_response[start:end]
    else:
        clean_json = text_response
        
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
