import streamlit as st
import requests
import json

st.set_page_config(page_title="WLED Controller", layout="wide")

st.title("WLED HTTP API Controller")

# Sidebar configuration
with st.sidebar:
    st.header("Connection Settings")
    wled_ip = st.text_input("WLED IP Address", value="192.168.1.100")
    wled_port = st.number_input("Port", value=80, min_value=1, max_value=65535)
    base_url = f"http://{wled_ip}:{wled_port}"

# Helper function for API calls
def api_call(endpoint, method="GET", data=None):
    try:
        url = f"{base_url}/{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        return response
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

# Tabs for different controls
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Device Info", "Power & Brightness", "Colors", "Effects", "Segments"])

# TAB 1: Device Information
with tab1:
    st.subheader("Device Information")
    if st.button("Fetch Device Info"):
        response = api_call("json/info")
        if response and response.status_code == 200:
            st.json(response.json())
        else:
            st.error("Failed to fetch device info")
    
    if st.button("Fetch Current State"):
        response = api_call("json/state")
        if response and response.status_code == 200:
            st.json(response.json())
        else:
            st.error("Failed to fetch state")

# TAB 2: Power and Brightness
with tab2:
    st.subheader("Power & Brightness Control")
    col1, col2 = st.columns(2)
    
    with col1:
        power = st.checkbox("Power ON", value=True)
        if st.button("Apply Power"):
            data = {"on": power}
            response = api_call("json", "POST", data)
            if response and response.status_code == 200:
                st.success("Power state updated")
            else:
                st.error("Failed to update power")
    
    with col2:
        brightness = st.slider("Brightness", 0, 255, 128)
        if st.button("Apply Brightness"):
            data = {"bri": brightness}
            response = api_call("json", "POST", data)
            if response and response.status_code == 200:
                st.success("Brightness updated")
            else:
                st.error("Failed to update brightness")

# TAB 3: Colors
with tab3:
    st.subheader("Color Control")
    color = st.color_picker("Pick a color", value="#FF0000")

    st.markdown("### Or enter RGB values")
    rgb_col1, rgb_col2, rgb_col3 = st.columns(3)
    with rgb_col1:
        r = st.number_input("R", min_value=0, max_value=255, value=255, step=1, key="rgb_r")
    with rgb_col2:
        g = st.number_input("G", min_value=0, max_value=255, value=0, step=1, key="rgb_g")
    with rgb_col3:
        b = st.number_input("B", min_value=0, max_value=255, value=0, step=1, key="rgb_b")

    use_manual_rgb = st.checkbox("Use RGB values instead of color picker", value=False)

    if use_manual_rgb:
        rgb = (r, g, b)
    else:
        rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # Multi-select segments
    segments = st.multiselect("Select Segments (0-3)", options=[0, 1, 2, 3], default=[0])

    if st.button("Apply Color"):
        if not segments:
            st.error("Please select at least one segment")
        else:
            seg_data = []
            for seg_id in segments:
                seg_data.append({"id": seg_id, "col": [list(rgb)]})
            data = {"seg": seg_data}
            response = api_call("json", "POST", data)
            if response and response.status_code == 200:
                st.success(f"Color updated for segments: {segments}")
            else:
                st.error("Failed to update color")

    st.write(f"Selected RGB: R={rgb[0]}, G={rgb[1]}, B={rgb[2]}")
    if use_manual_rgb:
        st.info("Using manual RGB values")
    else:
        st.info(f"Using color picker value {color}")

# TAB 4: Effects
with tab4:
    st.subheader("Effects Control")
    effect_id = st.number_input("Effect ID", value=0, min_value=0)
    speed = st.slider("Speed", 0, 255, 128)
    intensity = st.slider("Intensity", 0, 255, 128)

    # Allow applying effect to specific segments
    segments_fx = st.multiselect("Select Segments to apply effect (0-3)", options=[0, 1, 2, 3], default=[0])

    if st.button("Apply Effect"):
        if not segments_fx:
            st.error("Please select at least one segment")
        else:
            seg_list = []
            for seg_id in segments_fx:
                seg_list.append({
                    "id": seg_id,
                    "fx": effect_id,
                    "sx": speed,
                    "ix": intensity
                })
            data = {"seg": seg_list}
            response = api_call("json", "POST", data)
            if response and response.status_code == 200:
                st.success(f"Effect {effect_id} applied to segments: {segments_fx}")
            else:
                st.error("Failed to apply effect")

# TAB 5: Segments
with tab5:
    st.subheader("Segment Control")
    segment_id = st.number_input("Segment ID", value=0, min_value=0)
    start = st.number_input("Start LED", value=0, min_value=0)
    stop = st.number_input("Stop LED", value=30, min_value=1)
    brightness = st.slider("Segment Brightness", 0, 255, 128, key="seg_bri")
    
    if st.button("Apply Segment Settings"):
        data = {
            "seg": [{
                "id": segment_id,
                "start": start,
                "stop": stop,
                "bri": brightness
            }]
        }
        response = api_call("json", "POST", data)
        if response and response.status_code == 200:
            st.success("Segment updated")
        else:
            st.error("Failed to update segment")

st.sidebar.markdown("---")
st.sidebar.info(f"Connected to: {base_url}")