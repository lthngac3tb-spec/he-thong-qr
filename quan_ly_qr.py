import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os
import uuid

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

            # --- PHẦN CHỌN NGƯỜI CẦN GẶP THÔNG MINH ---
            danh_sach_nhom = ["Ban giám hiệu", "Đoàn trường", "GVCN", "Hành chính", "Khác"]
            lua_chon = st.selectbox("Bộ phận/Người cần gặp", danh_sach_nhom)
            
            # Khởi tạo các ô nhập bổ sung
            ten_lop = ""
            nguoi_cu_the = ""
            if lua_chon == "GVCN":
                ten_lop = st.text_input("Nhập tên lớp (Ví dụ: 12A1)")
            elif lua_chon == "Khác":
                nguoi_cu_the = st.text_input("Nhập tên người/bộ phận cụ thể")
            # ------------------------------------------

            submit = st.form_submit_button("Lấy mã QR")

            if submit:
                # Xử lý logic lấy giá trị cuối cùng để lưu
                if lua_chon == "GVCN":
                    chi_tiet_gap_ai = f"GVCN lớp {ten_lop}"
                elif lua_chon == "Khác":
                    chi_tiet_gap_ai = nguoi_cu_the
                else:
                    chi_tiet_gap_ai = lua_chon

                if name and phone and chi_tiet_gap_ai:
                    # Đoạn này là để lưu vào Excel của em
                    now = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                    new_data = pd.DataFrame({
                        "ID": [str(uuid.uuid4())[:8]],
                        "HoTen": [name],
                        "SDT": [phone],
                        "GapAi": [chi_tiet_gap_ai],
                        "GioVao": [now],
                        "GioRa": [""]
                    })
                    # Code lưu file Excel tiếp theo của em...
                    st.success(f"Đã đăng ký thành công gặp: {chi_tiet_gap_ai}")
                else:
                    st.error("Vui lòng nhập đầy đủ thông tin em nhé!")

    # PHẦN DÀNH CHO BẢO VỆ
   # --- PHẦN DÀNH CHO BẢO VỆ (Cập nhật mới) ---
else:
    st.title("🛡️ KHU VỰC QUẢN TRỊ")
    password = st.text_input("Nhập mật khẩu quản lý", type="password")
    
    if password == "123456": # Nhớ đổi mật khẩu của em ở đây
        st.success("Đã đăng nhập quyền Bảo vệ")
        
        df = pd.read_excel(FILE_NAME)
        # Chuyển cột GioVao sang định dạng ngày tháng để lọc nếu cần, ở đây mình lọc đơn giản
        
        # 1. DANH SÁCH KHÁCH ĐANG Ở TRONG (Chưa có giờ ra)
        st.subheader("🔴 Khách đang ở trong cơ quan")
        khach_trong = df[df['GioRa'].isna() | (df['GioRa'] == "")]
        if not khach_trong.empty:
            st.dataframe(khach_trong, use_container_width=True)
        else:
            st.info("Hiện không có khách nào ở trong.")

        st.divider()

        # 2. DANH SÁCH KHÁCH ĐÃ RA VỀ (Đã có giờ ra)
        st.subheader("🟢 Khách đã ra về trong ngày")
        khach_ve = df[df['GioRa'].notna() & (df['GioRa'] != "")]
        if not khach_ve.empty:
            # Đảo ngược danh sách để người mới về hiện lên đầu
            st.dataframe(khach_ve.iloc[::-1], use_container_width=True)
        else:
            st.info("Chưa có khách nào báo ra về.")
        
        st.divider()
        st.subheader("💾 Quản lý dữ liệu")
        
        # 1. Lấy ngày hiện tại để đặt tên file
        ngay_hien_tai = datetime.now().strftime("%d-%m-%Y")
        ten_file_xuat = f"Danh_sach_khach_{ngay_hien_tai}.xlsx"
        
        col1, col2 = st.columns(2)
        with col1:
            # 2. Mở file và tạo nút tải với tên file mới
            with open(FILE_NAME, "rb") as f:
                st.download_button(
                    label="📥 Tải File Excel Full", 
                    data=f, 
                    file_name=ten_file_xuat, # Tên file sẽ tự đổi theo ngày
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        with col2:
            if st.button("🗑️ Xóa toàn bộ dữ liệu (Reset)"):
                df_new = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "GioVao", "GioRa"])
                df_new.to_excel(FILE_NAME, index=False)
                st.warning("Đã xóa dữ liệu. Hãy F5 lại trang.")
    
    elif password != "":
        st.error("Sai mật khẩu rồi em!")








