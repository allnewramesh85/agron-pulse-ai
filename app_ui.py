# app_ui.py
import os
import streamlit as st
import httpx
from streamlit_js_eval import streamlit_js_eval

# 1. MOBILE RESPONSIVE LAYOUT CONFIGURATION
st.set_page_config(page_title="AgronPulse AI Client", layout="centered", initial_sidebar_state="collapsed")

# 2. IOS SYSTEM CONTRAST LOOK & FEEL CUSTOM CSS
st.markdown("""
    <style>
        @import url('https://googleapis.com');

        html, body, [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #112d15 0%, #07190a 100%) !important; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif; }
        .block-container { max-width: 480px !important; background: rgba(18, 43, 22, 0.85); backdrop-filter: blur(20px); border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1); margin: 1rem auto; padding: 1.5rem 1rem !important; }
        .brand-header { background: rgba(255, 255, 255, 0.04); padding: 15px; border-radius: 16px; text-align: center; margin-bottom: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.08); }
        .section-header { font-size: 1.05rem; font-weight: 600; color: #f1f5f9; margin: 1.4rem 0 0.6rem 0; letter-spacing: -0.2px; }

        /* iOS System Solid Blue Interaction Button */
        .stButton button { 
            width: 100% !important; 
            border-radius: 14px !important; 
            background: #007aff !important; 
            color: #ffffff !important; 
            font-weight: 600 !important; 
            font-size: 1rem !important;
            letter-spacing: -0.3px !important;
            padding: 0.75rem 1rem !important; 
            border: none !important;
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.25);
            transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .stButton button:hover {
            background: #1485ff !important;
            box-shadow: 0 6px 16px rgba(0, 122, 255, 0.35);
            transform: scale(0.99);
        }
        .stButton button:active {
            background: #0066d6 !important;
            transform: scale(0.97);
        }

        .insight-card { background: rgba(255, 255, 255, 0.04); border-radius: 14px; padding: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 12px; }
        .treatment-item { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
        .treatment-badge { background: rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 600; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }

        p, span, label, small, .stMarkdown { color: #94a3b8 !important; }
        h1, h2, h3, h4, h5, h6, strong { color: #ffffff !important; letter-spacing: -0.5px; }

        /* High-contrast iOS Theme Input box configurations */
        /* Enforces a solid black text color (#000000) inside text and numeric input boxes */
        div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
            background-color: rgba(255, 255, 255, 0.85) !important;
            color: #000000 !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            padding: 0.6rem 0.8rem !important;
            -webkit-text-fill-color: #000000 !important;
        }

        /* Retains black text visibility during active box targeting */
        div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {
            border: 2px solid #007aff !important;
            box-shadow: 0 0 0 1px #007aff !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
            background-color: #ffffff !important;
        }

        /* Target the input text placeholder styling directly */
        div[data-testid="stTextInput"] input::placeholder {
            color: rgba(0, 0, 0, 0.4) !important;
            -webkit-text-fill-color: rgba(0, 0, 0, 0.4) !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. NATIVE GEOLOCATION CAPTURE
gps_loc = streamlit_js_eval(
    data_string="navigator.geolocation.getCurrentPosition(p => {return {lat: p.coords.latitude, lng: p.coords.longitude}}, e => {return null})",
    target_id="agronpulseai_loc")

default_lat = 12.9716
default_lng = 77.5946

if gps_loc and isinstance(gps_loc, dict):
    if "lat" in gps_loc and gps_loc["lat"]: default_lat = float(gps_loc["lat"])
    if "lng" in gps_loc and gps_loc["lng"]: default_lng = float(gps_loc["lng"])

if "camera_active" not in st.session_state:
    st.session_state.camera_active = False

# 4. BRAND APP BANNER DESIGN
st.markdown(
    """<div class="brand-header"><h2>AgronPulse AI</h2><p style='margin:5px 0 0 0; opacity:0.6; font-size:0.8rem;'>Qualitative Diagnostics Structure</p></div>""",
    unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8080/api/v1/diagnose"
# BACKEND_URL = "http://127.0.0"
# 5. STEP 1: MULTI-MODAL DATA INGESTION
st.markdown('<div class="section-header">Ingest Media Target</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a: st.write("Input Mode Selector:")
with col_b:
    if st.button("Switch Mode"):
        st.session_state.camera_active = not st.session_state.camera_active
        st.rerun()

active_media, media_name, media_type = None, "leaf.jpg", "image/jpeg"
if st.session_state.camera_active:
    st.caption("Active Mode: Camera Recording")
    c_file = st.camera_input("Capture leaf")
    if c_file: active_media, media_name = c_file.read(), "camera.jpg"
else:
    st.caption("Active Mode: Multimedia File Upload")
    u_file = st.file_uploader("Upload file", type=["jpg", "jpeg", "png", "mp4", "mov"], label_visibility="collapsed")
    if u_file:
        active_media, media_name, media_type = u_file.read(), u_file.name, u_file.type
        file_ext = os.path.splitext(media_name)[0].lower()
        if file_ext in [".mp4", ".mov"]:
            st.video(u_file)
        else:
            st.image(u_file, width=True)

# 6. STEP 2: CONTEXTUAL FIELD NOTES
st.markdown('<div class="section-header">Qualitative Sign Details</div>', unsafe_allow_html=True)
query = st.text_input("Observed field anomalies:", value="Tomato leaves showing brown concentric ring markers.")

# 7. STEP 3: SPATIAL GEOLOCATION CONFIGURATION WITH OPTIONAL MANUAL OVERRIDE
st.markdown('<div class="section-header">Spatial Geolocation Parameters</div>', unsafe_allow_html=True)
st.caption("Coordinates automatically captured via device GPS sensor. Modify below to override manually.")

c1, c2 = st.columns(2)
with c1: lat = st.number_input("Latitude", value=default_lat, format="%.5f")
with c2: lng = st.number_input("Longitude", value=default_lng, format="%.5f")

# 8. TRANSMISSION PROCESSING PIPELINE
if st.button("AgronPulse Qualitative Signs"):
    if not active_media:
        st.error("Media input required.")
    else:
        with st.spinner("Decoding execution tracks..."):
            try:
                res = httpx.post(
                    BACKEND_URL,
                    data={"user_query": query, "latitude": str(lat), "longitude": str(lng),
                          "thread_id": "field_worker"},
                    files={"file": (media_name, active_media, media_type)},
                    timeout=300.0
                )
                if res.status_code == 200:
                    data = res.json()
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        st.markdown('<div class="section-header">Actionable Analysis Insights</div>',
                                    unsafe_allow_html=True)
                        st.markdown(
                            f"""<div class="insight-card" style="border-top:3px solid #007aff;"><small style="color:#94a3b8; text-transform:uppercase; font-size:0.7rem; font-weight:600;">Diagnosis</small><div style="font-size:1.2rem; font-weight:600; color:#ffffff; margin-top:2px;">{data.get('diagnosis', 'Unknown')}</div></div>""",
                            unsafe_allow_html=True)
                        rc1, rc2 = st.columns(2)
                        with rc1:
                            st.markdown(
                                f"""<div class="insight-card"><small style="color:#94a3b8; font-size:0.7rem; font-weight:500;">Confidence</small><div style="color:#ffffff; font-weight:600; margin-top:2px;">{data.get('confidence', 'Medium')}</div></div>""",
                                unsafe_allow_html=True)
                        with rc2:
                            st.markdown(
                                f"""<div class="insight-card"><small style="color:#94a3b8; font-size:0.7rem; font-weight:500;">Threat Risk</small><div style="color:#ffffff; font-weight:600; margin-top:2px;">{data.get('weather_risk_factor', 'UNKNOWN')}</div></div>""",
                                unsafe_allow_html=True)
                        st.markdown('<div class="section-header">Target Field Prescriptions</div>',
                                    unsafe_allow_html=True)
                        for idx, item in enumerate(data.get("actionable_treatments", []), 1):
                            st.markdown(
                                f"""<div class="treatment-item"><div class="treatment-badge">{idx}</div><div style="font-size:0.9rem; color:#f1f5f9;">{item}</div></div>""",
                                unsafe_allow_html=True)
                else:
                    st.error("Backend Error")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
