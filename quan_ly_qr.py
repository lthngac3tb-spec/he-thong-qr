import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os
from streamlit_qr_reader import qr_reader

# Cấu hình file lưu trữ
FILE_NAME = "danh_sach_khach.xlsx"

# Tạo file Excel nếu chưa có
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
    df.to_excel(FILE_NAME, index=False)

st.set_page_config(page_title="Hệ thống QR", layout="centered")
st.title("🏨 QUẢN LÝ KHÁCH RA VÀO")

tab1, tab2 = st.tabs(["📝 ĐĂNG KÝ VÀO", "🔍 QUÉT MÃ KHI VỀ"])

# --- TAB 1: KHÁCH ĐĂNG KÝ ---
with tab1:
    with st.form("form_vào"):
        name = st.text_input("Họ và tên")
        phone = st.text_input("Số điện thoại")
        target = st.text_input("Người cần gặp")
        purpose = st.text_area("Mục đích")
        submit = st.form_submit_button("Xác nhận và lấy mã QR")

    if submit and name:
        guest_id = f"G_{datetime.now().strftime('%d%H%M%S')}"
        time_in = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        
        # Lưu vào Excel
        df = pd.read_excel(FILE_NAME)
        new_data = pd.DataFrame([[guest_id, name, phone, target, purpose, time_in, ""]], columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(FILE_NAME, index=False)
        
        # Tạo mã QR
        qr_img = qrcode.make(guest_id)
        qr_img.save("guest_qr.png")
        st.success(f"Chào {name}! Bạn hãy chụp lại mã QR này:")
        st.image("guest_qr.png", width=250)

# --- TAB 2: BẢO VỆ QUÉT MÃ ---
with tab2:
    st.subheader("Bảo vệ quét mã của khách")
    # Sử dụng qr_reader để mở camera
    data_scan = qr_reader(key='qr_scanner')

    if data_scan:
        st.info(f"Đang kiểm tra mã: {data_scan}")
        df = pd.read_excel(FILE_NAME)
        
        # So khớp mã trong cột ID
        if data_scan in df['ID'].values:
            idx = df.index[df['ID'] == data_scan].tolist()[0]
            if pd.isna(df.at[idx, 'GioRa']) or df.at[idx, 'GioRa'] == "":
                df.at[idx, 'GioRa'] = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                df.to_excel(FILE_NAME, index=False)
                st.balloons()
                st.success(f"Xác nhận khách ra: {df.at[idx, 'HoTen']}")
            else:
                st.warning("Khách này đã báo ra rồi.")
        else:
            st.error("Mã không hợp lệ.")

    # Nút tải báo cáo
    st.divider()
    with open(FILE_NAME, "rb") as f:
        st.download_button("📥 Tải File Excel Báo Cáo", f, file_name=FILE_NAME)
