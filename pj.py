import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Coral Heat Stress Monitor", layout="wide")
st.title("🌊 Coral Heat Stress Monitor")
st.markdown("ระบบวิเคราะห์อุณหภูมิผิวน้ำทะเลและคำนวณความเสี่ยงปะการังฟอกขาวในพื้นที่หลัก")

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

st.sidebar.header("📍 ตั้งค่าการตรวจสอบ")
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
        st.subheader(f"แนวโน้มอุณหภูมิย้อนหลังที่ {selected_name}")
        st.line_chart(df_result.set_index('Time')['Sea_Surface_Temp'])

    # CSV 
    csv_filename = "marine_data_output.csv"
    df_result.to_csv(csv_filename, index=False)
    st.divider()
    st.write("💾 **พรีวิวข้อมูลที่สกัดได้:**")
    st.dataframe(df_result.tail(5))
    