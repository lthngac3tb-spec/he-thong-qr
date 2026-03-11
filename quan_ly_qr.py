import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os
import uuid
from io import BytesIO

# Cấu hình file
FILE_NAME = "danh_sach_khach.xlsx"

# --- ĐOẠN CODE ĐÓN ĐẦU KHÁCH QUÉT MÃ QR ĐỂ CHECK-OUT ---
params = st.query_params
if "action" in params and params["action"] == "checkout":
    target_id = params.get("id")
    st.title("🚀 XÁC NHẬN RA VỀ")
    if os.path.exists(FILE_NAME):
        df = pd.read_excel(FILE_NAME)
        if target_id in df['ID'].astype(str).values:
            mask = (df['ID'].astype(str) == target_id) & (df['GioRa'].isna() | (df['GioRa'] == ""))
            if mask.any():
                df.loc[mask, 'GioRa'] = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                df.to_excel(FILE_NAME, index=False)
                st.success("✅ Cảm ơn quý khách! Hệ thống đã ghi nhận giờ ra về thành công.")
                st.balloons()
            else:
                st.warning("⚠️ Mã này đã báo ra trước đó rồi.")
        else:
            st.error("❌ Không tìm thấy mã định danh này.")
    st.stop() 

# Khởi tạo file nếu chưa có (Thêm cột MucDich)
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
    df.to_excel(FILE_NAME, index=False)

st.set_page_config(page_title="Hệ thống QR", layout="centered")

# --- GIAO DIỆN CHÍNH ---
st.sidebar.title("🔑 QUẢN TRỊ")
user_role = st.sidebar.selectbox("Bạn là ai?", ["Khách hàng", "Bảo vệ / Admin"])

if user_role == "Khách hàng":
    st.title("📝 ĐĂNG KÝ LIÊN HỆ CÔNG TÁC")
    
    name = st.text_input("Họ và tên")
    phone = st.text_input("Số điện thoại")

    danh_sach_nhom = ["Ban giám hiệu", "Đoàn trường", "GVCN", "Hành chính", "Khác"]
    lua_chon = st.selectbox("Bộ phận/Người cần gặp", danh_sach_nhom)
    
    chi_tiet_gap_ai = ""
    muc_dich_cv = "" # Khởi tạo biến mục đích

    # Logic hiển thị thêm ô nhập dựa trên lựa chọn
    if lua_chon == "GVCN":
        ten_lop = st.text_input("Nhập tên lớp (Ví dụ: 12A1)")
        chi_tiet_gap_ai = f"GVCN lớp {ten_lop}"
    elif lua_chon == "Hành chính":
        chi_tiet_gap_ai = "Phòng Hành chính"
        # HIỆN Ô MỤC ĐÍCH KHI CHỌN HÀNH CHÍNH
        muc_dich_cv = st.text_area("🎯 Mục đích công việc (Bắt buộc):", placeholder="Ví dụ: Nộp hồ sơ, Công chứng...")
    elif lua_chon == "Khác":
        nguoi_cu_the = st.text_input("Nhập tên người/bộ phận cụ thể")
        chi_tiet_gap_ai = nguoi_cu_the
    else:
        chi_tiet_gap_ai = lua_chon

    if st.button("Lấy mã QR"):
        check_ok = True
        # Kiểm tra thông tin cơ bản
        if not name or not phone:
            st.error("Vui lòng nhập Họ tên và Số điện thoại!")
            check_ok = False
        # Kiểm tra mục đích nếu gặp Hành chính
        elif lua_chon == "Hành chính" and not muc_dich_cv:
            st.error("⚠️ Vui lòng nhập mục đích công việc để bộ phận Hành chính tiếp đón tốt nhất!")
            check_ok = False
        elif lua_chon == "GVCN" and "ten_lop" in locals() and not ten_lop:
            st.error("Vui lòng nhập tên lớp!")
            check_ok = False

        if check_ok:
            now = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
            new_id = str(uuid.uuid4())[:8]
            
            # Đọc file hiện tại để concat
            df_current = pd.read_excel(FILE_NAME)
            
            new_row = {
                "ID": new_id,
                "HoTen": name,
                "SDT": phone,
                "GapAi": chi_tiet_gap_ai,
                "MucDich": muc_dich_cv, # Lưu mục đích vào đây
                "GioVao": now,
                "GioRa": ""
            }
            
            df_current = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)
            df_current.to_excel(FILE_NAME, index=False)
            
            st.success(f"Đã đăng ký thành công!")

            # Tạo QR
            link_goc = "https://he-thong-qr-yq76udatzyox4wdfbr8n6q.streamlit.app/"
            link_bao_ra = f"{link_goc}?action=checkout&id={new_id}"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(link_bao_ra)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buf = BytesIO()
            img.save(buf, format="PNG")
            st.divider()
            st.image(buf.getvalue(), caption=f"Mã định danh: {new_id}", use_container_width=True)
            st.info("💡 Quý khách chụp màn hình QR này để quét khi ra về!")

# --- PHẦN DÀNH CHO BẢO VỆ ---
else:
    st.title("🛡️ KHU VỰC QUẢN TRỊ")
    password = st.text_input("Nhập mật khẩu quản lý", type="password")
    
    if password == "123456":
        df = pd.read_excel(FILE_NAME)
        
        st.subheader("🔴 Khách đang ở trong cơ quan")
        khach_trong = df[df['GioRa'].isna() | (df['GioRa'] == "")]
        st.dataframe(khach_trong, use_container_width=True)

        st.divider()
        st.subheader("🟢 Khách đã ra về")
        khach_ve = df[df['GioRa'].notna() & (df['GioRa'] != "")]
        st.dataframe(khach_ve.iloc[::-1], use_container_width=True)
        
        # Nút tải file
        with open(FILE_NAME, "rb") as f:
            st.download_button("📥 Tải File Excel Full", data=f, file_name="Dach_sach_khach.xlsx")
            
    elif password != "":
        st.error("Sai mật khẩu!")
