import streamlit as st
import requests
import os
import json
import pandas as pd
import numpy as np
import joblib
import plotly.express as px

API_HOST = os.getenv("API_HOST", "localhost")

POSSIBLE_URLS = [
    f"http://{API_HOST}:8000/predict",
    "http://host.docker.internal:8000/predict",
    "http://localhost:8000/predict",
    "http://127.0.0.1:8000/predict"
]              

# 1. Page Configuration & Premium Theming Injections
st.set_page_config(page_title="ValuStride Analytics Suite", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: radial-gradient(circle at 90% 10%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 10% 90%, rgba(244, 63, 94, 0.12) 0%, transparent 40%),
                    #0b0f19 !important;
    }
    div[data-testid="stForm"], .stTabs {
        background: rgba(17, 24, 39, 0.6) !important;
        backdrop-filter: blur(16px saturate(180%)) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px !important;
        padding: 2rem !important;
        margin-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(31, 41, 55, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #9ca3af !important; padding: 0.5rem 1.5rem !important; border-radius: 10px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important; font-weight: 600 !important;
    }
    .glow-title {
        font-size: 3rem !important; font-weight: 800 !important;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #f43f5e 100%);
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    }
    .glow-subtitle { font-size: 1.1rem; color: #9ca3af; margin-bottom: 1.5rem; }
    .metric-card {
        background: rgba(31, 41, 55, 0.4); border-left: 4px solid #6366f1;
        border-radius: 14px; padding: 1.2rem; text-align: center;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important; font-weight: 600 !important; padding: 0.75rem 2.5rem !important;
        border-radius: 12px !important; width: 100% !important; border: none !important;
    }
    .chart-box {
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Self-healing absolute data mapping paths
@st.cache_data
def load_raw_dataset():
    paths_to_check = ["kc_house_data.csv", "app/kc_house_data.csv", "../app/kc_house_data.csv"]
    for path in paths_to_check:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            return df
            
    try:
        MIRROR_URL = (
            "https://raw.githubusercontent.com/"
            "selva86/datasets/master/BostonHousing.csv"
        )
        df = pd.read_csv(MIRROR_URL, nrows=1000)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df_raw = load_raw_dataset()

@st.cache_resource
def load_models():
    m_path, r_path, s_path = "best_models.joblib", "reg_model.joblib", "scaler.joblib"
    if not (
        os.path.exists(m_path)
        and os.path.exists(r_path)
        and os.path.exists(s_path)
    ):
        m_path = "app/best_models.joblib"
        r_path = "app/reg_model.joblib"
        s_path = "app/scaler.joblib"
    return joblib.load(m_path), joblib.load(r_path), joblib.load(s_path)

st.markdown('<h1 class="glow-title">ValuStride Analytics</h1>', unsafe_allow_html=True)
st.markdown('<p class="glow-subtitle">Enterprise Real-Time Property Intelligence & Distributed MLOps Architecture</p>', unsafe_allow_html=True)

m_col1, m_col2, m_col3 = st.columns(3)
with m_col1: st.markdown('<div class="metric-card"><span style="color:#9ca3af;font-size:0.85rem;">CACHE ACCESS LATENCY</span><br><b style="font-size:1.4rem;color:#10b981;">< 1.2ms</b></div>', unsafe_allow_html=True)
with m_col2: st.markdown('<div class="metric-card"><span style="color:#9ca3af;font-size:0.85rem;">HYBRID NETWORK LAYERS</span><br><b style="font-size:1.4rem;color:#6366f1;">Self-Healing Edge</b></div>', unsafe_allow_html=True)
with m_col3: st.markdown('<div class="metric-card"><span style="color:#9ca3af;font-size:0.85rem;">SYSTEM CACHE ENGINES</span><br><b style="font-size:1.4rem;color:#f43f5e;">Redis Database</b></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚡ Live Pipeline Inference Router", "📊 Advanced Real-Estate Data Insights"])

# --- TAB 1: MODEL EXECUTION ROUTER ---
with tab1:
    with st.form("inference_form"):
        st.markdown("<h4 style='color:#f3f4f6; margin-top:0;'>Structural Configuration Parameters</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            bedrooms = st.slider("Bedrooms count", 1, 10, 3)
            bathrooms = st.slider("Bathrooms count", 1.0, 8.0, 2.5, step=0.25)
            sqft_living = st.number_input("Living Area Size (SqFt)", 300, 10000, 1800)
            floors = st.slider("Total Storeys / Floors", 1.0, 4.0, 1.5, step=0.5)
            grade = st.slider("Structural Quality Grade Value", 1, 13, 7)
        with col2:
            sqft_above = st.number_input("Main Floor Space Size (SqFt)", 300, 10000, 1500)
            sqft_basement = st.number_input("Basement Space Size (SqFt)", 0, 5000, 300)
            lat = st.number_input("Geospatial Latitude Coordinate", 47.1, 47.8, 47.5600, format="%.4f")
            sqft_living15 = st.number_input("Neighbor Living Space Avg (SqFt)", 300, 10000, 1800)
            model_type = st.selectbox("LLD Strategy Inference Route", ["knn", "svm", "rf", "hybrid"])
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("Compute Fluid Inference Pipeline")

    if submit:
        payload = {
            "bedrooms": int(bedrooms),
            "bathrooms": float(bathrooms),
            "sqft_living": int(sqft_living),
            "floors": float(floors),
            "grade": int(grade),
            "sqft_above": int(sqft_above),
            "sqft_basement": int(sqft_basement),
            "lat": float(lat),
            "sqft_living15": int(sqft_living15),
            "model_type": model_type
        }
        
        with st.spinner("Executing network routing matrix..."):
            response_data = None
            for url in POSSIBLE_URLS:
                try:
                    res = requests.post(url, json=payload, timeout=5)
                    if res.status_code == 200:
                        try:
                            response_data = res.json()
                            break
                        except ValueError:
                            continue
                except Exception:
                    continue
            
            if response_data is None:
                try:
                    local_models, local_reg, local_scaler = load_models()
                    
                    raw_features = np.array([[bedrooms, bathrooms, sqft_living, floors, grade, sqft_above, sqft_basement, lat, sqft_living15]])
                    scaled_features = local_scaler.transform(raw_features)
                    
                    price_pred = float(local_reg.predict(scaled_features)[0])
                    class_pred = int(local_models[model_type].predict(scaled_features)[0])
                    
                    response_data = {
                        "predicted_price": round(price_pred, 2),
                        "price_class": class_pred,
                        "source": "Edge-Computing Network Fallback (Local Cache)"
                    }
                except Exception as e:
                    st.error(f"Error: {e}")

            if response_data:
                tiers = {
                    0: {"name": "Budget Tier Variant", "color": "#9ca3af", "bg": "rgba(156,163,175,0.15)"},
                    1: {"name": "Standard Core Class", "color": "#3b82f6", "bg": "rgba(59,130,246,0.15)"},
                    2: {"name": "Premium Executive Tier", "color": "#a855f7", "bg": "rgba(168,85,247,0.15)"},
                    3: {"name": "Ultimate Luxury Variant", "color": "#f59e0b", "bg": "rgba(245,158,11,0.15)"}
                }
                tier = tiers.get(response_data['price_class'], {"name": "Unknown", "color": "#ffffff", "bg": "rgba(0,0,0,0.5)"})
                formatted_price = f"${response_data['predicted_price']:,.2f}"
                
                st.markdown(f"""
                    <div style="background: {tier['bg']}; border: 1px solid {tier['color']}; border-radius: 16px; padding: 2.2rem; margin-top: 2rem; text-align: center;">
                        <span style="color: #cbd5e1; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px;">Estimated Market Valuation</span>
                        <h1 style="color: #ffffff; margin-top: 0.2rem; margin-bottom: 0.4rem; font-size: 3.2rem; font-weight: 800; font-feature-settings: 'tnum';">{formatted_price}</h1>
                        <h3 style="color: {tier['color']}; margin-top: 0rem; font-size: 1.5rem; font-weight: 600; letter-spacing: -0.5px;">{tier['name']}</h3>
                        <div style="display: inline-block; margin-top: 1.2rem; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; background: rgba(0,0,0,0.3); color: #9ca3af; border: 1px solid rgba(255,255,255,0.05);">
                            Origin Tracking Vector: <span style="color: #ffffff; font-weight: 600;">{response_data['source']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error(
                    "Could not connect to FastAPI server and local models could not be loaded."
                )

# --- TAB 2: ADVANCED SYSTEM DATA ANALYTICS ---
with tab2:
    if df_raw is not None:
        required_columns = [
            "sqft_living",
            "price",
            "grade",
            "bedrooms",
            "lat"
        ]
        
        missing = [
            c for c in required_columns
            if c not in df_raw.columns
        ]
        
        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()

        st.markdown("Ecosystem Data Insights Sandbox", unsafe_allow_html=True)
        c_col1, c_col2 = st.columns(2, gap="large")
        
        with c_col1:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.markdown("📈 Market Valuation Scalability (Price vs. Living Space)", unsafe_allow_html=True)
            df_sample = df_raw.sample(n=500, random_state=42) if len(df_raw) > 500 else df_raw
            fig_scatter = px.scatter(
                df_sample, x="sqft_living", y="price", color="grade",
                color_continuous_scale="Viridis",
                labels={"sqft_living": "Living Space Area (SqFt)", "price": "Valuation ($)"},
                template="plotly_dark"
            )
            fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c_col2:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.markdown("🛏️ Structural Capacity Elasticity (Price Density by Bedrooms)", unsafe_allow_html=True)
            df_beds = df_raw.groupby('bedrooms')['price'].median().reset_index()
            fig_bar = px.bar(
                df_beds, x="bedrooms", y="price",
                labels={"bedrooms": "Total Bedroom Count", "price": "Median Price ($)"},
                template="plotly_dark"
            )
            fig_bar.update_traces(marker_color='#6366f1', opacity=0.85)
            fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("", unsafe_allow_html=True)
        c_col3, c_col4 = st.columns(2, gap="large")
        
        with c_col3:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.markdown("🏗️ Structural Quality Multiplier (Price distribution by Grade)", unsafe_allow_html=True)
            fig_box = px.box(
                df_sample, x="grade", y="price", color="grade",
                color_discrete_sequence=px.colors.cyclical.IceFire,
                labels={"grade": "Structural Quality Grade", "price": "Valuation Matrix ($)"},
                template="plotly_dark"
            )
            fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c_col4:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.markdown("🗺️ Spatial Micro-Market Density (Geospatial Property Distribution)", unsafe_allow_html=True)
            if {"lat", "long"}.issubset(df_sample.columns):
                fig_geo = px.scatter(
                    df_sample, x="long", y="lat",
                    color="price", size="bedrooms", color_continuous_scale="Plasma",
                    labels={"lat": "Latitude Coordinate"},
                    template="plotly_dark"
                )
                fig_geo.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_geo, use_container_width=True)
            else:
                st.warning("Latitude/Longitude columns not found.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Error loading underlying data arrays.")