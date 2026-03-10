import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os
from streamlit_camera_qrcode_reader import qrcode_reader

# Cấu hình file
FILE_NAME = "danh_sach_khach.xlsx"
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
    df.to_excel(FILE_NAME, index=False)

st.set_page_config(page_title="Hệ thống QR STEM", layout="centered")
st.title("🏨 QUẢN LÝ RA VÀO THÔNG MINH")

tab1, tab2 = st.tabs(["📝 KHÁCH ĐĂNG KÝ", "🔍 BẢO VỆ QUÉT MÃ"])

# --- TAB 1: KHÁCH ĐĂNG KÝ ---
with tab1:
    with st.form("checkin_form"):
        name = st.text_input("Họ và tên khách")
        phone = st.text_input("Số điện thoại")
        target = st.text_input("Người cần gặp")
        purpose = st.text_area("Mục đích")
        btn = st.form_submit_button("Lấy mã QR vào cổng")

    if btn and name:
        guest_id = f"GUEST_{datetime.now().strftime('%d%H%M%S')}"
        now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        
        # Lưu vào Excel
        df = pd.read_excel(FILE_NAME)
        new_row = pd.DataFrame([[guest_id, name, phone, target, purpose, now, ""]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(FILE_NAME, index=False)
        
        # Tạo QR rõ nét
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(guest_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("current_qr.png")
        
        st.success(f"Chào {name}! Mã QR của bạn đây:")
        st.image("current_qr.png", caption="Chụp màn hình mã này để check-out khi về")

# --- TAB 2: BẢO VỆ QUÉT MÃ ---
with tab2:
    st.subheader("Quét mã QR của khách khi về")
    # Sử dụng thư viện quét trực tiếp từ Camera
    qrcode_data = qrcode_reader(key='qrcode_reader')

    if qrcode_data:
        st.warning(f"Đã đọc được mã: {qrcode_data}")
        df = pd.read_excel(FILE_NAME)
        
        if qrcode_data in df['ID'].values:
            idx = df.index[df['ID'] == qrcode_data].tolist()[0]
            if pd.isna(df.at[idx, 'GioRa']) or df.at[idx, 'GioRa'] == "":
                df.at[idx, 'GioRa'] = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                df.to_excel(FILE_NAME, index=False)
                st.balloons()
                st.success(f"XÁC NHẬN: Khách {df.at[idx, 'HoTen']} đã ra về!")
            else:
                st.info("Khách này đã báo ra trước đó.")
        else:
            st.error("Mã QR không có trong danh sách.")

    st.divider()
    if st.checkbox("Xem danh sách khách hôm nay"):
        st.dataframe(pd.read_excel(FILE_NAME))
