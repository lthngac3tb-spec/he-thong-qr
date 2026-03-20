import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime, timedelta # Thêm timedelta để chỉnh giờ VN
import os
import uuid
from io import BytesIO

# Cấu hình file
FILE_NAME = "danh_sach_khach.xlsx"

# 1. KHỞI TẠO FILE NẾU CHƯA CÓ
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich/Lop", "GioVao", "GioRa"])
    df.to_excel(FILE_NAME, index=False)

st.set_page_config(page_title="Hệ thống QR Khách - THPT Thác Bà", layout="centered")

# --- PHẦN XỬ LÝ CHECK-OUT QUA QR ---
params = st.query_params
if "action" in params and params["action"] == "checkout":
    target_id = params.get("id")
    st.title("🚀 XÁC NHẬN RA VỀ")
    
    if os.path.exists(FILE_NAME):
        df = pd.read_excel(FILE_NAME)
        mask = (df['ID'].astype(str) == target_id) & (df['GioRa'].isna() | (df['GioRa'] == ""))
        
        if mask.any():
            ten_khach = df.loc[mask, 'HoTen'].values[0]
            # Lấy giờ VN chuẩn
            gio_ra_vn = datetime.utcnow() + timedelta(hours=7)
            df.loc[mask, 'GioRa'] = gio_ra_vn.strftime("%H:%M %d/%m/%Y")
            df.to_excel(FILE_NAME, index=False)
            
            st.balloons() 
            st.markdown(f"""
                <div style="background-color: #ffffff; padding: 30px; border-radius: 20px; border: 3px solid #008000; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); margin: 20px 0; text-align: center;">
                    <h1 style="color: #008000; margin-bottom: 5px;">🏫 THPT THÁC BÀ</h1>
                    <hr style="border: 1px solid #eee; width: 50%; margin: 10px auto;">
                    <h2 style="color: #2E7D32; font-weight: bold;"> CẢM ƠN QUÝ KHÁCH ĐÃ GHÉ THĂM</h2>
                    <h3 style="color: #555;">HẸN GẶP LẠI!</h3>
                    <div style="background-color: #e8f5e9; padding: 10px; border-radius: 10px; display: inline-block; margin-top: 15px;">
                        <p style="margin: 0; color: #1b5e20; font-weight: bold;">Khách hàng: {ten_khach}</p>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">Giờ ra hệ thống: {gio_ra_vn.strftime("%H:%M")}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.success(f"✅ Đã xác nhận ra về thành công!")
        else:
            already_out = (df['ID'].astype(str) == target_id) & (df['GioRa'].notna())
            if already_out.any():
                st.info("💡 Bạn đã xác nhận ra về trước đó rồi. Chúc bạn một ngày tốt lành!")
            else:
                st.error("❌ Mã không hợp lệ hoặc không tồn tại.")
    
    if st.button("Quay lại trang đăng ký"):
        st.query_params.clear()
        st.rerun()
    st.stop()

# --- GIAO DIỆN CHÍNH ---
st.sidebar.title("🔑 QUẢN TRỊ")
user_role = st.sidebar.selectbox("Bạn là ai?", ["Khách hàng", "Bảo vệ / Admin"])

if user_role == "Khách hàng":
    st.title("📝 ĐĂNG KÝ VÀO CƠ QUAN")
    # Chèn Logo trường vào đây nếu em muốn
    # st.image("link_logo.png", width=120) 
    
    name = st.text_input("Họ và tên")
    phone = st.text_input("Số điện thoại")
    bo_phan = st.selectbox("Bộ phận cần gặp", ["Ban giám hiệu", "Hành chính", "GVCN", "Khác"])
    
    muc_dich = ""
    if bo_phan == "Hành chính":
        muc_dich = st.text_area("🎯 Mục đích công việc (Bắt buộc):")
    if bo_phan == "GVCN":
        muc_dich = st.text_area("Lớp:")
    if st.button("Lấy mã QR"):
        if name and phone:
            if bo_phan == "Hành chính" and not muc_dich:
                st.error("Vui lòng nhập mục đích!")
            else:
                new_id = str(uuid.uuid4())[:8]
                df_curr = pd.read_excel(FILE_NAME)
                # Giờ vào Việt Nam
                gio_vao_vn = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M %d/%m")
                
                new_row = {
                    "ID": new_id, "HoTen": name, "SDT": phone, 
                    "GapAi": bo_phan, "MucDich": muc_dich, 
                    "GioVao": gio_vao_vn, "GioRa": ""
                }
                df_curr = pd.concat([df_curr, pd.DataFrame([new_row])], ignore_index=True)
                df_curr.to_excel(FILE_NAME, index=False)
                
                link_goc = "https://he-thong-quan-ly-khach-ra-vao.streamlit.app/" 
                qr_img = qrcode.make(f"{link_goc}?action=checkout&id={new_id}")
                buf = BytesIO()
                qr_img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="Quét mã này khi ra về", width=300)
        else:
            st.error("Vui lòng nhập đủ tên và SĐT!")


else:
    st.title("🛡️ KHU VỰC QUẢN TRỊ")
    
    # Sử dụng key để Streamlit theo dõi thay đổi ngay lập tức
    password = st.text_input("Nhập mật khẩu quản lý", type="password", key="admin_password")
    
    # Kiểm tra mật khẩu trực tiếp (Streamlit sẽ tự chạy lại mỗi khi em gõ thêm 1 ký tự)
    if password == "123456":
        st.success("🔓 Xác thực thành công! Đang mở bảng điều khiển...")
        
        # --- TOÀN BỘ CODE QUẢN TRỊ NẰM TRONG ĐÂY ---
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            
         
            
  
            
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            st.subheader("🔴 Khách đang ở trong cơ quan")
            khach_trong = df[df['GioRa'].isna() | (df['GioRa'] == "")]
            if not khach_trong.empty:
                st.dataframe(khach_trong, use_container_width=True)
            else:
                st.info("Hiện không có khách nào ở trong.")
            
            st.divider()
            st.subheader("🟢 Khách đã ra về trong ngày")
            khach_ve = df[df['GioRa'].notna() & (df['GioRa'] != "")]
            if not khach_ve.empty:
                st.dataframe(khach_ve.iloc[::-1], use_container_width=True)
            
            st.divider()
            # Phần xuất Excel của em thầy giữ nguyên lề lối nhé
            st.subheader("📝 Công cụ báo cáo")
            from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
            from openpyxl.utils import get_column_letter
            from openpyxl import Workbook
            import io

            if st.button("📊 Chuẩn bị file Excel"):
                ngay_hien_tai = (datetime.utcnow() + timedelta(hours=7)).strftime("%d_%m_%Y")
                buffer = io.BytesIO()
                wb = Workbook()
                ws = wb.active
                ws.title = "BaoCaoRaVao"
                headers = list(df.columns)
                ws.append(headers)
                for r in df.values.tolist():
                    row_data = [str(x) if str(x) != 'nan' else "" for x in r]
                    ws.append(row_data)
                
                blue_fill = PatternFill(start_color="B8CCE4", end_color="B8CCE4", fill_type="solid")
                thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
                for col_num in range(1, len(headers) + 1):
                    cell = ws.cell(row=1, column=col_num)
                    cell.fill = blue_fill
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = thin_border
                
                for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                    for cell in row:
                        cell.border = thin_border
                
                wb.save(buffer)
                st.download_button(label="📥 Tải file về máy", data=buffer.getvalue(), file_name=f"Bao_cao_{ngay_hien_tai}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif password != "":
        # Chỉ báo lỗi khi độ dài mật khẩu đã đủ nhưng sai (để tránh báo lỗi ngay từ ký tự đầu tiên)
        if len(password) >= 6:
            st.error("❌ Mật khẩu không chính xác!")
