import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os
from streamlit_qrcode_scanner import qrcode_scanner

# 1. Khởi tạo file Excel nếu chưa có
FILE_NAME = "danh_sach_khach.xlsx"
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
    df.to_excel(FILE_NAME, index=False)

st.title("🏨 HỆ THỐNG QUẢN LÝ RA VÀO")

# Tạo 2 tab: Cho Khách và Cho Bảo vệ
tab1, tab2 = st.tabs(["Khách Đăng Ký (Vào)", "Bảo Vệ Quét (Về)"])

# --- PHẦN 1: KHÁCH ĐĂNG KÝ ---
with tab1:
    st.header("Đăng ký vào cơ quan")
    with st.form("form_checkin"):
        name = st.text_input("Họ và tên")
        phone = st.text_input("Số điện thoại")
        target = st.text_input("Gặp ai?")
        purpose = st.text_area("Mục đích công tác")
        submit = st.form_submit_button("Xác nhận vào")

    if submit:
        # Tạo ID và giờ vào
        guest_id = f"QR_{datetime.now().strftime('%d%m%y_%H%M%S')}"
        check_in_time = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        
        # Lưu vào file Excel
        new_data = pd.DataFrame([[guest_id, name, phone, target, purpose, check_in_time, ""]], 
                                columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
        df = pd.read_excel(FILE_NAME)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(FILE_NAME, index=False)
        
        # Tạo mã QR
        qr_img = qrcode.make(guest_id)
        qr_img.save("guest_qr.png")
        
        st.success(f"Đăng ký thành công! ID của bạn là: {guest_id}")
        st.image("guest_qr.png", caption="HÃY CHỤP MÀN HÌNH MÃ NÀY ĐỂ CHECK-OUT KHI VỀ")

# --- PHẦN 2: BẢO VỆ CHECK-OUT ---
with tab2:
    st.header("🔍 Bảo vệ quét mã khi khách ra")
    st.info("Hướng camera điện thoại vào mã QR của khách")
    
    # Mở camera để quét mã QR
    # Khi quét thành công, nó sẽ tự trả về cái ID của khách vào biến 'captured_id'
    captured_id = qrcode_scanner(key='scanner_checkout')

    if captured_id:
        st.warning(f"Đã nhận diện mã: {captured_id}")
        
        # Đọc dữ liệu từ Excel
        df = pd.read_excel(FILE_NAME)
        
        # Kiểm tra ID có trong danh sách không
        if captured_id in df['ID'].values:
            idx = df.index[df['ID'] == captured_id].tolist()[0]
            
            # Kiểm tra xem khách đã báo ra chưa
            if pd.isna(df.at[idx, 'GioRa']) or df.at[idx, 'GioRa'] == "":
                df.at[idx, 'GioRa'] = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                df.to_excel(FILE_NAME, index=False)
                st.balloons() # Bắn pháo hoa chúc mừng
                st.success(f"✅ KHÁCH RA THÀNH CÔNG: {df.at[idx, 'HoTen']}")
            else:
                st.info("Mã này đã ghi nhận giờ ra trước đó rồi.")
        else:
            st.error("❌ Mã QR này không có trong hệ thống hoặc không đúng định dạng!")

    # Hiển thị bảng danh sách phía dưới để bảo vệ theo dõi
    st.divider()
    st.subheader("📊 Danh sách thực tế")
    st.dataframe(pd.read_excel(FILE_NAME))

# Hiển thị bảng dữ liệu thực tế cho bảo vệ xem
  
    st.divider()
    st.subheader("📊 Danh sách khách ra vào")
    
# Đọc lại file Excel để đảm bảo dữ liệu mới nhất
    try:
        df_view = pd.read_excel(FILE_NAME)
        # Sắp xếp để người mới vào hiện lên đầu cho dễ nhìn
        st.dataframe(df_view.sort_index(ascending=False), use_container_width=True)
    except:
        st.write("Chưa có dữ liệu khách nào.")

