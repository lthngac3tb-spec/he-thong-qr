import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os

# Cấu hình file
FILE_NAME = "danh_sach_khach.xlsx"
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "GioVao", "GioRa"])
    df.to_excel(FILE_NAME, index=False)

st.set_page_config(page_title="Hệ thống QR", layout="centered")

# --- XỬ LÝ QUÉT QR QUA LINK (CHECK-OUT TỰ ĐỘNG) ---
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
            st.success(f"✅ XÁC NHẬN: Khách {df.at[idx, 'HoTen']} đã ra về!")
        else:
            st.info("Mã này đã báo ra rồi.")
    if st.button("Trở về trang đăng ký"):
        st.query_params.clear()
    st.stop() # Dừng lại không hiện phần dưới nếu đang trong chế độ checkout

# --- GIAO DIỆN CHÍNH ---
st.sidebar.title("🔑 QUẢN TRỊ")
user_role = st.sidebar.selectbox("Bạn là ai?", ["Khách hàng", "Bảo vệ / Admin"])

if user_role == "Khách hàng":
    st.title("📝 ĐĂNG KÝ VÀO CỔNG")
    with st.form("checkin_form"):
        name = st.text_input("Họ và tên")
        phone = st.text_input("Số điện thoại")
        target = st.text_input("Người cần gặp")
        submit = st.form_submit_button("Lấy mã QR")

    if submit and name:
        guest_id = f"G_{datetime.now().strftime('%d%H%M%S')}"
        time_in = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        
        df = pd.read_excel(FILE_NAME)
        new_row = pd.DataFrame([[guest_id, name, phone, target, time_in, ""]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(FILE_NAME, index=False)
        
        # Link để quét ra (Nhớ sửa link app của em cho đúng nhé)
        app_url = "https://he-thong-qr-yq76udatzyox4wdfbr8n6q.streamlit.app/"
        checkout_url = f"{app_url}?checkout_id={guest_id}"
        
        qr_img = qrcode.make(checkout_url)
        qr_img.save("guest_qr.png")
        st.success("Đăng ký thành công! Hãy chụp lại mã này để đưa bảo vệ khi về:")
        st.image("guest_qr.png", width=300)

else:
    # PHẦN DÀNH CHO BẢO VỆ
    st.title("🛡️ KHU VỰC QUẢN TRỊ")
    password = st.text_input("Nhập mật khẩu quản lý", type="password")
    
    # Mật khẩu em tự đặt (ví dụ: 123456)
    if password == "123456":
        st.success("Đã đăng nhập quyền Bảo vệ")
        
        st.subheader("📊 Danh sách khách đang ở trong")
        df = pd.read_excel(FILE_NAME)
        # Chỉ hiện những người chưa ra về
        khach_trong = df[df['GioRa'].isna() | (df['GioRa'] == "")]
        st.table(khach_trong)
        
        st.divider()
        st.subheader("💾 Tải dữ liệu máy chủ")
        with open(FILE_NAME, "rb") as f:
            st.download_button("📥 Tải File Excel Full", f, file_name=FILE_NAME)
    elif password != "":
        st.error("Sai mật khẩu rồi em ơi!")

