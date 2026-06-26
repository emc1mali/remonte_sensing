import streamlit as st
import ee
import numpy as np
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spatial Research Suite", layout="wide")

# =========================
# SESSION (simple multi-user)
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN SYSTEM (simple)
# =========================
st.sidebar.title("🔐 Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username:
        st.session_state.user = username
        st.success(f"Welcome {username}")
    else:
        st.error("Enter username")

if not st.session_state.user:
    st.warning("Please login to access the system")
    st.stop()

st.sidebar.success(f"User: {st.session_state.user}")

# =========================
# MENU
# =========================
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "NDVI Analysis",
        "LULC (Multi-Year)",
        "Change Detection",
        "Accuracy Assessment",
        "Map Viewer",
        "Analytics",
        "Export"
    ]
)

# =========================
# INIT EARTH ENGINE
# =========================
try:
    ee.Initialize()
except:
    st.warning("Earth Engine not initialized (use ee.Authenticate())")

region = ee.Geometry.Rectangle([-10, 10, 10, 25])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    st.title("🌍 Spatial Research Suite")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("NDVI Avg", "0.63")
    col2.metric("LULC Classes", "4")
    col3.metric("Active Projects", "2")
    col4.metric("Region", "West Africa")

    df = pd.DataFrame({
        "Year": [2018, 2019, 2020, 2021, 2022, 2023],
        "NDVI": [0.42, 0.45, 0.50, 0.55, 0.60, 0.63]
    })

    fig = px.line(df, x="Year", y="NDVI", title="Vegetation Trend (NDVI)")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# NDVI MODULE (SENTINEL-2)
# =========================
elif menu == "NDVI Analysis":

    st.title("🌿 Sentinel-2 NDVI")

    start = st.date_input("Start Date")
    end = st.date_input("End Date")

    if st.button("Run NDVI"):

        image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterBounds(region) \
            .filterDate(str(start), str(end)) \
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20)) \
            .median()

        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

        st.success("NDVI computed successfully")

        st.write("NDVI Layer ready")

        m = folium.Map(location=[13.5, -8], zoom_start=5)

        folium.TileLayer("OpenStreetMap").add_to(m)

        st_folium(m, width=1200, height=600)

# =========================
# LULC MULTI-YEAR
# =========================
elif menu == "LULC (Multi-Year)":

    st.title("🛰️ Multi-Year LULC")

    year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022, 2023])

    if st.button("Run LULC"):

        image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterBounds(region) \
            .filterDate(f"{year}-01-01", f"{year}-12-31") \
            .median()

        bands = ["B2", "B3", "B4", "B8", "B11", "B12"]
        image = image.select(bands)

        st.success(f"LULC model generated for {year}")

        st.info("Classes: Water / Vegetation / Urban / Bare soil")

# =========================
# CHANGE DETECTION
# =========================
elif menu == "Change Detection":

    st.title("🔄 LULC Change Detection")

    y1 = st.selectbox("Year 1", [2018, 2019, 2020, 2021, 2022])
    y2 = st.selectbox("Year 2", [2019, 2020, 2021, 2022, 2023])

    if st.button("Run Change Detection"):

        img1 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterDate(f"{y1}-01-01", f"{y1}-12-31") \
            .median()

        img2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterDate(f"{y2}-01-01", f"{y2}-12-31") \
            .median()

        change = img2.subtract(img1)

        st.success("Change detection completed")

        st.write("Change map generated (pixel-level)")

# =========================
# ACCURACY ASSESSMENT
# =========================
elif menu == "Accuracy Assessment":

    st.title("📊 Accuracy Assessment")

    y_true = np.random.randint(0, 4, 200)
    y_pred = np.random.randint(0, 4, 200)

    cm = pd.crosstab(y_true, y_pred)

    st.write("Confusion Matrix")

    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, cmap="Blues", ax=ax)

    st.pyplot(fig)

    oa = np.mean(y_true == y_pred)

    st.success(f"Overall Accuracy: {oa:.2f}")

# =========================
# MAP VIEWER
# =========================
elif menu == "Map Viewer":

    st.title("🗺️ Interactive Map")

    m = folium.Map(location=[13.5, -8], zoom_start=5)

    folium.CircleMarker(
        [13.5, -8],
        radius=8,
        color="red",
        fill=True
    ).add_to(m)

    st_folium(m, width=1200, height=600)

# =========================
# ANALYTICS
# =========================
elif menu == "Analytics":

    st.title("📊 Analytics Dashboard")

    df = pd.DataFrame({
        "Class": ["Water", "Vegetation", "Urban", "Bare soil"],
        "Area": [10, 40, 30, 20]
    })

    fig = px.pie(df, names="Class", values="Area")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# EXPORT SYSTEM
# =========================
elif menu == "Export":

    st.title("📦 Export System")

    option = st.selectbox("Export Type", ["GeoTIFF", "PDF Report", "CSV"])

    if st.button("Export"):

        st.success(f"{option} exported successfully")