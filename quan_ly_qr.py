import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os
import uuid
from io import BytesIO

# Cấu hình file
FILE_NAME = "danh_sach_khach.xlsx"
# --- ĐOẠN CODE ĐÓN ĐẦU KHÁCH QUÉT MÃ QR ĐỂ CHECK-OUT (BƯỚC 2) ---
# Lấy các tham số từ địa chỉ web (URL)
params = st.query_params

if "action" in params and params["action"] == "checkout":
    target_id = params.get("id")
    
    st.title("🚀 XÁC NHẬN RA VỀ")
    st.info(f"Đang xử lý cho khách có mã ID: {target_id}")
    
    # Đọc file để cập nhật giờ ra
    if os.path.exists(FILE_NAME):
        df = pd.read_excel(FILE_NAME)
        # Kiểm tra xem ID có tồn tại trong cột 'ID' không
        if target_id in df['ID'].astype(str).values:
            # Tìm dòng có ID đó và chưa có giờ ra (GioRa trống)
            mask = (df['ID'].astype(str) == target_id) & (df['GioRa'].isna() | (df['GioRa'] == ""))
            
            if mask.any():
                # Ghi giờ ra hiện tại
                df.loc[mask, 'GioRa'] = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                df.to_excel(FILE_NAME, index=False)
                
                st.success("✅ Cảm ơn quý khách! Hệ thống đã ghi nhận giờ ra về thành công.")
                st.balloons() # Bắn pháo hoa chúc mừng
                st.info("Xin chào và hẹn gặp lại!")
            else:
                st.warning("⚠️ Mã này đã báo ra trước đó rồi hoặc không cần báo lại.")
        else:
            st.error("❌ Không tìm thấy mã định danh này trong danh sách.")
    
    # Cực kỳ quan trọng: Dừng toàn bộ các lệnh bên dưới lại
    st.stop() 
# -------------------------------------------------------------
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
        
        # Nhập thông tin cơ bản
        name = st.text_input("Họ và tên")
        phone = st.text_input("Số điện thoại")

        # Lựa chọn người cần gặp
        danh_sach_nhom = ["Ban giám hiệu", "Đoàn trường", "GVCN", "Hành chính", "Khác"]
        lua_chon = st.selectbox("Bộ phận/Người cần gặp", danh_sach_nhom)
        
        chi_tiet_gap_ai = ""
        ten_lop = ""
        nguoi_cu_the = ""

        if lua_chon == "GVCN":
            ten_lop = st.text_input("Nhập tên lớp (Ví dụ: 12A1)")
            chi_tiet_gap_ai = f"GVCN lớp {ten_lop}"
        elif lua_chon == "Khác":
            nguoi_cu_the = st.text_input("Nhập tên người/bộ phận cụ thể")
            chi_tiet_gap_ai = nguoi_cu_the
        else:
            chi_tiet_gap_ai = lua_chon

        # Nút bấm đăng ký
        if st.button("Lấy mã QR"):
            # Kiểm tra xem khách đã nhập đủ thông tin chưa
            check_ok = True
            if not name or not phone:
                check_ok = False
                st.error("Vui lòng nhập Họ tên và Số điện thoại!")
            elif lua_chon == "GVCN" and not ten_lop:
                check_ok = False
                st.error("Vui lòng nhập tên lớp!")
            elif lua_chon == "Khác" and not nguoi_cu_the:
                check_ok = False
                st.error("Vui lòng nhập tên người cần gặp cụ thể!")

            if check_ok:
                # 1. Tạo dữ liệu mới
                now = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                new_id = str(uuid.uuid4())[:8]
                new_data = pd.DataFrame({
                    "ID": [new_id],
                    "HoTen": [name],
                    "SDT": [phone],
                    "GapAi": [chi_tiet_gap_ai],
                    "GioVao": [now],
                    "GioRa": [""]
                })
                
                # 2. Lưu vào Excel
                df = pd.read_excel(FILE_NAME)
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_excel(FILE_NAME, index=False)
                
                st.success(f"Đã đăng ký thành công gặp: {chi_tiet_gap_ai}")

                # 3. TẠO VÀ HIỂN THỊ QR (Phần này phải nằm ở đây mới đúng)
               # --- ĐOẠN CODE TẠO QR THÔNG MINH (BƯỚC 1) ---
                link_goc = "https://he-thong-qr-yq76udatzyox4wdfbr8n6q.streamlit.app/"
    # Thêm ?action=checkout để máy biết đây là lệnh "Báo ra"
                link_bao_ra = f"{link_goc}?action=checkout&id={new_id}"
                
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(link_bao_ra)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                buf = BytesIO()
                img.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.divider()
                st.image(byte_im, caption=f"Mã định danh: {new_id}", use_container_width=True)
                st.info("💡 Quý khách vui lòng lưu lại mã QR này để check out nhé!")

    # PHẦN DÀNH CHO BẢO VỆ
   # --- PHẦN DÀNH CHO BẢO VỆ (Cập nhật mới) ---
else:
    st.title("🛡️ KHU VỰC QUẢN TRỊ")
    password = st.text_input("Nhập mật khẩu quản lý", type="password")
    
    if password == "123456":
        st.success("🛡️ Đã đăng nhập quyền Bảo vệ/Quản trị")
        
        # Đọc dữ liệu từ file Excel
        df = pd.read_excel(FILE_NAME)
        
        # --- 1. HIỂN THỊ DANH SÁCH KHÁCH ĐANG Ở TRONG ---
        st.subheader("🔴 Khách đang ở trong cơ quan")
        # Lọc những người chưa có Giờ Ra (GioRa trống)
        khach_trong = df[df['GioRa'].isna() | (df['GioRa'] == "")]
        if not khach_trong.empty:
            st.dataframe(khach_trong, use_container_width=True)
        else:
            st.info("Hiện không có khách nào ở trong.")

        st.divider()

        # --- 2. HIỂN THỊ DANH SÁCH KHÁCH ĐÃ RA VỀ ---
        st.subheader("🟢 Khách đã ra về trong ngày")
        # Lọc những người đã có Giờ Ra
        khach_ve = df[df['GioRa'].notna() & (df['GioRa'] != "")]
        if not khach_ve.empty:
            # iloc[::-1] để người mới về hiện lên đầu cho dễ nhìn
            st.dataframe(khach_ve.iloc[::-1], use_container_width=True)
        else:
            st.info("Chưa có khách nào báo ra về.")
        
        st.divider()
        
        # --- 3. QUẢN LÝ DỮ LIỆU ---
        st.subheader("💾 Công cụ quản lý")
        
        # Lấy ngày hiện tại để đặt tên file tải về
        ngay_hien_tai = datetime.now().strftime("%d-%m-%Y")
        ten_file_xuat = f"Danh_sach_khach_{ngay_hien_tai}.xlsx"
        
        col1, col2 = st.columns(2)
        with col1:
            with open(FILE_NAME, "rb") as f:
                st.download_button(
                    label="📥 Tải File Excel Full", 
                    data=f, 
                    file_name=ten_file_xuat,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        with col2:
            if st.button("🗑️ Xóa dữ liệu (Reset ngày mới)"):
                df_new = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "GioVao", "GioRa"])
                df_new.to_excel(FILE_NAME, index=False)
                st.warning("Đã xóa toàn bộ dữ liệu. Hãy F5 trang web.")
    
    elif password != "":
        st.error("Sai mật khẩu rồi em!")



















