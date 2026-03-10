import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os

FILE_NAME = "danh_sach_khach.xlsx"
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
    df.to_excel(FILE_NAME, index=False)

st.set_page_config(page_title="Hệ thống QR", layout="centered")

# --- KIỂM TRA NẾU CÓ MÃ ID TRÊN LINK (Dành cho Bảo vệ quét) ---
query_params = st.query_params
if "checkout_id" in query_params:
    checkout_id = query_params["checkout_id"]
    df = pd.read_excel(FILE_NAME)
    if checkout_id in df['ID'].values:
        idx = df.index[df['ID'] == checkout_id].tolist()[0]
        if pd.isna(df.at[idx, 'GioRa']) or df.at[idx, 'GioRa'] == "":
            df.at[idx, 'GioRa'] = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            df.to_excel(FILE_NAME, index=False)
            st.balloons()
            st.success(f"XÁC NHẬN RA VỀ: Khách {df.at[idx, 'HoTen']} thành công!")
        else:
            st.info("Mã này đã xác nhận ra trước đó rồi.")
    else:
        st.error("Mã không hợp lệ.")
    if st.button("Quay lại trang chính"):
        st.query_params.clear()

# --- GIAO DIỆN CHÍNH ---
st.title("🏨 QUẢN LÝ RA VÀO")
tab1, tab2 = st.tabs(["📝 ĐĂNG KÝ VÀO", "📊 DANH SÁCH"])

with tab1:
    with st.form("form_vào"):
        name = st.text_input("Họ và tên")
        phone = st.text_input("Số điện thoại")
        target = st.text_input("Người cần gặp")
        submit = st.form_submit_button("Lấy mã QR")

    if submit and name:
        guest_id = f"G_{datetime.now().strftime('%d%H%M%S')}"
        time_in = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        
        # Lưu vào Excel
        df = pd.read_excel(FILE_NAME)
        new_data = pd.DataFrame([[guest_id, name, phone, target, "Đăng ký", time_in, ""]], columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(FILE_NAME, index=False)
        
        # TẠO LINK XÁC NHẬN RA (Link của app em + ID khách)
        # Thay link dưới đây bằng link app thực tế của em
        app_url = "https://he-thong-qr-n4rgxnkpvjqua3egyw6wfz.streamlit.app/"
        checkout_url = f"{app_url}?checkout_id={guest_id}"
        
        # Tạo QR chứa cái link đó
        qr_img = qrcode.make(checkout_url)
        qr_img.save("guest_qr.png")
        st.success(f"Chào {name}! Đưa mã này cho bảo vệ khi ra về:")
        st.image("guest_qr.png", width=300)

with tab2:
    st.subheader("Danh sách khách")
    st.dataframe(pd.read_excel(FILE_NAME))
    with open(FILE_NAME, "rb") as f:
        st.download_button("📥 Tải File Excel", f, file_name=FILE_NAME)
