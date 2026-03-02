import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Coral Heat Stress Monitor", layout="wide")
navy_color = "#0B3F7C"
st.markdown("""
    <style>
        /* เปลี่ยนสีพื้นหลังของ Sidebar เป็น Navy Marine */
        [data-testid="stSidebar"] {
            background-color: #0B3F7C;
        }
    </style>
    """, unsafe_allow_html=True)
st.markdown(f"""
    <h1 style='color: {navy_color}; text-align: center;'>
        🌊 Coral Heat Stress Monitor
    </h1>
    """, unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: black; font-size: 18px;'>ระบบติดตามอุณหภูมิผิวน้ำทะเลและคำนวณความเสี่ยงปะการังฟอกขาวในพื้นที่หลัก</p>", unsafe_allow_html=True)

andaman_locs = {
    "หมู่เกาะสุรินทร์ (พังงา)": {"lat": 9.42, "lon": 97.87, "avg_max": 29.5},
    "หมู่เกาะสิมิลัน (พังงา)": {"lat": 8.65, "lon": 97.64, "avg_max": 29.4},
    "ภูเก็ต (ราไวย์)": {"lat": 7.77, "lon": 98.32, "avg_max": 29.8},
    "เกาะหลีเป๊ะ (สตูล)": {"lat": 6.49, "lon": 99.30, "avg_max": 29.5}
}

gulf_locs = {
    "เกาะล้าน (ชลบุรี)": {"lat": 12.91, "lon": 100.77, "avg_max": 30.2},
    "เกาะเสม็ด (ระยอง)": {"lat": 12.56, "lon": 101.45, "avg_max": 30.1},
    "เกาะเต่า (สุราษฎร์ฯ)": {"lat": 10.10, "lon": 99.83, "avg_max": 30.0},
    "หมู่เกาะอ่างทอง (สุราษฎร์ฯ)": {"lat": 9.62, "lon": 99.67, "avg_max": 29.9}
}

st.sidebar.header("เลือกฝั่งและสถานที่")
region = st.sidebar.radio("เลือกฝั่งทะเล", ["ฝั่งอันดามัน", "ฝั่งอ่าวไทย"])

if region == "ฝั่งอันดามัน":
    selected_name = st.sidebar.selectbox("เลือกสถานที่", list(andaman_locs.keys()))
    loc = andaman_locs[selected_name]
else:
    selected_name = st.sidebar.selectbox("เลือกสถานที่", list(gulf_locs.keys()))
    loc = gulf_locs[selected_name]


def scrape_marine_data(lat, lon):
    # ดึงข้อมูลผ่าน API 
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=sea_surface_temperature&past_days=7"
    response = requests.get(url).json()
    df = pd.DataFrame({
        'Time': response['hourly']['time'],
        'Sea_Surface_Temp': response['hourly']['sea_surface_temperature'],
        'Location': selected_name
    })
    return df

if st.button('start'):
    df_result = scrape_marine_data(loc['lat'], loc['lon'])
    current_temp = df_result['Sea_Surface_Temp'].iloc[-1]
    threshold = loc['avg_max'] + 1.0  # เกณฑ์ความทนทาน

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("อุณหภูมิปัจจุบัน", f"{current_temp} °C")
        if current_temp >= threshold:
            st.error("🔴 วิกฤต: เสี่ยงฟอกขาวสูง")
        elif current_temp >= loc['avg_max']:
            st.warning("🟡 เฝ้าระวัง: อุณหภูมิสูงกว่าค่าเฉลี่ย")
        else:
            st.success("🟢 ปกติ: สภาพแวดล้อมปลอดภัย")
        st.map(pd.DataFrame({'lat': [loc['lat']], 'lon': [loc['lon']]}))
    
    with col2:
        st.markdown(f"""
    <h3 style='color: #0B3F7C;'>แนวโน้มอุณหภูมิย้อนหลังที่ {selected_name}</h3>
    """, unsafe_allow_html=True)
        st.line_chart(df_result.set_index('Time')['Sea_Surface_Temp'])

    # CSV 
    csv_filename = "marine_data_output.csv"
    df_result.to_csv(csv_filename, index=False)
    st.divider()
    st.write("💾 **พรีวิวข้อมูลที่สกัดได้:**")
    st.dataframe(df_result.tail(5))

# เปลี่ยนสีเฉยๆ
st.markdown("""
    <style>
        /* 1. เปลี่ยนสีพื้นหลัง Sidebar */
        [data-testid="stSidebar"] {
            background-color: #002147;
        }

        /* 2. เจาะจงเปลี่ยนสี 'เลือกฝั่งและสถานที่' (หัวข้อใหญ่ใน Sidebar) */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            color: white !important;
        }

        /* 3. เจาะจงเปลี่ยนสี 'เลือกฝั่งทะเล', 'ฝั่งอันดามัน', 'ฝั่งอ่าวไทย' และ 'เลือกสถานที่' */
        [data-testid="stSidebar"] label p, 
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stWidgetLabel"] p {
            color: white !important;
        }

        /* 4. ล็อคสีข้อความในกล่อง Selectbox ให้เป็นสีดำตามเดิม (ไม่แตะต้อง) */
        div[data-baseweb="select"] > div {
            color: #31333F !important;
        }
    </style>
    """, unsafe_allow_html=True)