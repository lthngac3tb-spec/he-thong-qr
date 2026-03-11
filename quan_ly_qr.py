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

# --- PHẦN BẢO VỆ & XUẤT FILE ĐẸP ---
else:
    st.title("🛡️ QUẢN LÝ KHÁCH")
    pwd = st.text_input("Mật khẩu", type="password")
    if pwd == "123456":
        df_view = pd.read_excel(FILE_NAME)
        st.subheader("📊 Danh sách khách trong ngày")
        st.dataframe(df_view, use_container_width=True)

        st.divider()
        st.subheader("💾 Xuất báo cáo chuyên nghiệp")

        # --- LOGIC XUẤT FILE EXCEL ĐẸP (DÙNG XLSXWRITER) ---
        buffer = BytesIO()
        try:
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_view.to_excel(writer, index=False, sheet_name='BaoCaoKhach')
                workbook  = writer.book
                worksheet = writer.sheets['BaoCaoKhach']

                # Định dạng Header
                header_fmt = workbook.add_format({
                    'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter',
                    'fg_color': '#B8CCE4', 'font_color': '#000000'
                })

                # Định dạng Nội dung
                cell_fmt = workbook.add_format({'border': 1, 'valign': 'vcenter'})

                # Vẽ Header
                for col_num, value in enumerate(df_view.columns.values):
                    worksheet.write(0, col_num, value, header_fmt)
                
                # Vẽ Data & Kẻ bảng
                for row_num in range(1, len(df_view) + 1):
                    for col_num in range(len(df_view.columns)):
                        val = df_view.iloc[row_num-1, col_num]
                        worksheet.write(row_num, col_num, str(val) if pd.notna(val) else "", cell_fmt)

                # Tự động chỉnh độ rộng cột
                for i, col in enumerate(df_view.columns):
                    width = max(df_view[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, width)

            st.download_button(
                label="📥 Tải Báo Cáo Khách (File đẹp)",
                data=buffer.getvalue(),
                file_name=f"Bao_cao_khach_{datetime.now().strftime('%d-%m')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Lỗi xuất file: {e}")
