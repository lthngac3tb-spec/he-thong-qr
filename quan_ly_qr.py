import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os
import uuid
from io import BytesIO

# Cấu hình file
FILE_NAME = "danh_sach_khach.xlsx"

# 1. KHỞI TẠO FILE NẾU CHƯA CÓ
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
    df.to_excel(FILE_NAME, index=False)

st.set_page_config(page_title="Hệ thống QR Khách", layout="centered")

# --- PHẦN XỬ LÝ CHECK-OUT QUA QR  ---
params = st.query_params
if "action" in params and params["action"] == "checkout":
    target_id = params.get("id")
    st.title("🚀 XÁC NHẬN RA VỀ")
    df = pd.read_excel(FILE_NAME)
    mask = (df['ID'].astype(str) == target_id) & (df['GioRa'].isna() | (df['GioRa'] == ""))
    if mask.any():
        df.loc[mask, 'GioRa'] = datetime.now().strftime("%H:%M %d/%m/%Y")
        df.to_excel(FILE_NAME, index=False)
        st.success("✅ Cảm ơn quý khách! Đã ghi nhận giờ ra.")
        st.balloons()
    else:
        st.warning("Mã này đã báo ra hoặc không tồn tại.")
    st.stop()

# --- GIAO DIỆN CHÍNH ---
st.sidebar.title("🔑 QUẢN TRỊ")
user_role = st.sidebar.selectbox("Bạn là ai?", ["Khách hàng", "Bảo vệ / Admin"])

if user_role == "Khách hàng":
    st.title("📝 ĐĂNG KÝ VÀO CƠ QUAN")
    name = st.text_input("Họ và tên")
    phone = st.text_input("Số điện thoại")
    bo_phan = st.selectbox("Bộ phận cần gặp", ["Ban giám hiệu", "Hành chính", "Kế toán", "Khác"])
    
    muc_dich = ""
    if bo_phan == "Hành chính":
        muc_dich = st.text_area("🎯 Mục đích công việc (Bắt buộc):")
    
    if st.button("Lấy mã QR"):
        if name and phone:
            if bo_phan == "Hành chính" and not muc_dich:
                st.error("Vui lòng nhập mục đích!")
            else:
                new_id = str(uuid.uuid4())[:8]
                df_curr = pd.read_excel(FILE_NAME)
                new_row = {
                    "ID": new_id, "HoTen": name, "SDT": phone, 
                    "GapAi": bo_phan, "MucDich": muc_dich, 
                    "GioVao": datetime.now().strftime("%H:%M %d/%m"), "GioRa": ""
                }
                df_curr = pd.concat([df_curr, pd.DataFrame([new_row])], ignore_index=True)
                df_curr.to_excel(FILE_NAME, index=False)
                
                # Tạo QR (Thay link của em vào đây nhé)
                link_goc = "https://he-thong-quan-ly-khach-ra-vao.streamlit.app/" 
                qr_img = qrcode.make(f"{link_goc}?action=checkout&id={new_id}")
                buf = BytesIO()
                qr_img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="Quét mã này khi ra về", width=300)
        else:
            st.error("Vui lòng nhập đủ tên và SĐT!")

# --- PHẦN DÀNH CHO BẢO VỆ (Giữ nguyên logic cũ, chỉ nâng cấp xuất file) ---
else:
    st.title("🛡️ KHU VỰC QUẢN TRỊ")
    password = st.text_input("Nhập mật khẩu quản lý", type="password")
    
    if password == "123456":
        st.success("🛡️ Đã đăng nhập quyền Bảo vệ/Quản trị")
        
        # Đọc dữ liệu từ file Excel hiện tại
        df = pd.read_excel(FILE_NAME)
        
        st.subheader("🔴 Khách đang ở trong cơ quan")
        khach_trong = df[df['GioRa'].isna() | (df['GioRa'] == "")]
        st.dataframe(khach_trong, use_container_width=True)

        st.divider()

        st.subheader("🟢 Khách đã ra về trong ngày")
        khach_ve = df[df['GioRa'].notna() & (df['GioRa'] != "")]
        st.dataframe(khach_ve.iloc[::-1], use_container_width=True)
        
        st.divider()
        
        # --- ĐOẠN NÂNG CẤP XUẤT FILE ĐẸP ---
        st.subheader("💾 Công cụ quản lý")
        
        # 1. Tạo tên file có ngày hiện tại
        ngay_hien_tai = datetime.now().strftime("%d-%m-%Y")
        ten_file_xuat = f"Danh_sach_khach_{ngay_hien_tai}.xlsx"
        
        # 2. Logic tạo file Excel trang trí đẹp
        buffer = BytesIO()
        # Sử dụng xlsxwriter để kẻ bảng và tô màu
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Bao_cao')
            
            workbook  = writer.book
            worksheet = writer.sheets['Bao_cao']

            # Định dạng Tiêu đề (Header)
            header_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D7E4BC' # Màu xanh lá nhạt
            })

            # Định dạng Nội dung (Cells)
            cell_format = workbook.add_format({
                'border': 1,
                'align': 'left',
                'valign': 'vcenter'
            })

            # Vẽ lại Header với định dạng
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Vẽ lại dữ liệu và kẻ bảng từng ô
            for row_num in range(1, len(df) + 1):
                for col_num in range(len(df.columns)):
                    # Lấy giá trị, nếu nan thì để rỗng
                    val = df.iloc[row_num-1, col_num]
                    if pd.isna(val): val = ""
                    worksheet.write(row_num, col_num, str(val), cell_format)

            # Tự động chỉnh độ rộng cột
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)

        # 3. Nút tải file
        st.download_button(
            label="📥 Tải File Excel Báo Cáo (Đã kẻ bảng)",
            data=buffer.getvalue(),
            file_name=ten_file_xuat,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Nút Reset dữ liệu (Giữ nguyên của em)
        if st.button("🗑️ Xóa dữ liệu (Reset ngày mới)"):
            df_new = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
            df_new.to_excel(FILE_NAME, index=False)
            st.warning("Đã xóa dữ liệu. Hãy F5 trang web.")
            
    elif password != "":
        st.error("Sai mật khẩu rồi em!")

