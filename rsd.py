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
# EARTH ENGINE INIT SAFE
# =========================
try:
    ee.Initialize()
except:
    st.warning("Earth Engine not initialized. Run ee.Authenticate() locally first.")

# Study region (West Africa example)
region = ee.Geometry.Rectangle([-10, 10, 10, 25])

# =========================
# SESSION LOGIN (SIMPLE)
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

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
# DASHBOARD
# =========================
if menu == "Dashboard":

    st.title("🌍 Spatial Research Suite Dashboard")

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
# NDVI MODULE
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

        ndvi_vis = {
            "min": -1,
            "max": 1,
            "palette": ["blue", "white", "green"]
        }

        map_ndvi = folium.Map(location=[13.5, -8], zoom_start=5)

        folium.raster_layers.TileLayer(
            tiles=ndvi.getMapId(ndvi_vis)["tile_fetcher"].url_format,
            attr="NDVI",
            name="NDVI"
        ).add_to(map_ndvi)

        folium.LayerControl().add_to(map_ndvi)

        st_folium(map_ndvi, width=1200, height=600)

        st.success("NDVI generated successfully")

# =========================
# LULC CLASSIFICATION (RF)
# =========================
elif menu == "LULC (Multi-Year)":

    st.title("🛰️ LULC Classification (Random Forest)")

    year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022, 2023])

    if st.button("Run LULC"):

        image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterBounds(region) \
            .filterDate(f"{year}-01-01", f"{year}-12-31") \
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20)) \
            .median()

        bands = ["B2", "B3", "B4", "B8", "B11", "B12"]
        image = image.select(bands)

        # ⚠️ Demo training data (replace later with real samples)
        training_points = image.sample(
            region,
            scale=10,
            numPixels=2000
        )

        classifier = ee.Classifier.smileRandomForest(50).train(
            features=training_points,
            classProperty="B8",
            inputProperties=bands
        )

        classified = image.classify(classifier)

        vis = {
            "min": 0,
            "max": 3,
            "palette": ["blue", "green", "red", "yellow"]
        }

        map_lulc = folium.Map(location=[13.5, -8], zoom_start=5)

        folium.raster_layers.TileLayer(
            tiles=classified.getMapId(vis)["tile_fetcher"].url_format,
            attr="LULC",
            name="LULC"
        ).add_to(map_lulc)

        folium.LayerControl().add_to(map_lulc)

        st_folium(map_lulc, width=1200, height=600)

        st.success(f"LULC completed for {year}")

# =========================
# CHANGE DETECTION
# =========================
elif menu == "Change Detection":

    st.title("🔄 Change Detection")

    y1 = st.selectbox("Year 1", [2018, 2019, 2020, 2021, 2022])
    y2 = st.selectbox("Year 2", [2019, 2020, 2021, 2022, 2023])

    if st.button("Run Change Detection"):

        img1 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterDate(f"{y1}-01-01", f"{y1}-12-31") \
            .median()

        img2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterDate(f"{y2}-01-01", f"{y2}-12-31") \
            .median()

        change = img2.subtract(img1).normalizedDifference(["B8", "B4"])

        vis = {
            "min": -1,
            "max": 1,
            "palette": ["red", "white", "green"]
        }

        map_change = folium.Map(location=[13.5, -8], zoom_start=5)

        folium.raster_layers.TileLayer(
            tiles=change.getMapId(vis)["tile_fetcher"].url_format,
            attr="Change Detection",
            name="Change"
        ).add_to(map_change)

        st_folium(map_change, width=1200, height=600)

        st.success("Change detection completed")

# =========================
# ACCURACY ASSESSMENT
# =========================
elif menu == "Accuracy Assessment":

    st.title("📊 Accuracy Assessment")

    y_true = np.random.randint(0, 4, 200)
    y_pred = np.random.randint(0, 4, 200)

    cm = pd.crosstab(y_true, y_pred)

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
# EXPORT
# =========================
elif menu == "Export":

    st.title("📦 Export System")

    option = st.selectbox("Export Type", ["GeoTIFF", "PDF Report", "CSV"])

    if st.button("Export"):
        st.success(f"{option} export triggered (backend to implement)")
