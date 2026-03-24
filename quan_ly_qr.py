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
                    <h2 style="color: #008000; margin-bottom: 5px;font-size: 1.5rem">🏫 THPT THÁC BÀ</h2>
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
                    "GapAi": bo_phan, "MucDich/Lop": muc_dich, 
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


# --- PHẦN DÀNH CHO BẢO VỆ / ADMIN ---
else:
    st.title("🛡️ KHU VỰC QUẢN TRỊ")
    
    # 1. Tạo hộp rỗng để chứa ô nhập mật khẩu
    login_placeholder = st.empty()
    password = login_placeholder.text_input("Nhập mật khẩu quản lý", type="password", key="admin_password")
    
    if password == "123456":
        # 2. Xóa ô mật khẩu ngay khi đúng
        login_placeholder.empty()
        st.success("🔓 Xác thực thành công! Chào mừng cán bộ trực ban.")
        
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            
            # --- HIỂN THỊ CÁC BẢNG DỮ LIỆU ---
            st.subheader("🔴 Khách đang ở trong cơ quan")
            khach_trong = df[df['GioRa'].isna() | (df['GioRa'] == "")]
            st.dataframe(khach_trong, use_container_width=True)

            st.divider()
            st.subheader("🟢 Khách đã ra về")
            khach_ve = df[df['GioRa'].notna() & (df['GioRa'] != "")]
            st.dataframe(khach_ve.iloc[::-1], use_container_width=True)

            # --- CÔNG CỤ XUẤT FILE & RESET ---
            st.divider()
            st.subheader("⚙️ CÔNG CỤ HỆ THỐNG")
            
            col1, col2 = st.columns(2)
            
    
            with col1:
                if st.button("📊 Chuẩn bị file Excel"):
                    from datetime import datetime, timedelta
                    import io
                    import base64
                    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
                    from openpyxl.utils import get_column_letter

                    # 1. Lấy ngày hiện tại VN
                    ngay_hien_tai = (datetime.utcnow() + timedelta(hours=7)).strftime("%d_%m_%Y")
                    file_name = f"Bao_cao_{ngay_hien_tai}.xlsx"
                
                    # 2. Tạo file Excel vào bộ nhớ đệm
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Danh_Sach_Khach')
                        
                        # --- BẮT ĐẦU PHẦN ĐỊNH DẠNG ---
                        workbook = writer.book
                        worksheet = writer.sheets['Danh_Sach_Khach']
                        
                        # Định dạng font và màu sắc cho Tiêu đề (Dòng 1)
                        header_fill = PatternFill(start_color="0070C0", end_color="0070C0", fill_type="solid")
                        header_font = Font(color="FFFFFF", bold=True, size=12)
                        alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                                        top=Side(style='thin'), bottom=Side(style='thin'))

                        for col_num, column_title in enumerate(df.columns, 1):
                            cell = worksheet.cell(row=1, column=col_num)
                            cell.fill = header_fill
                            cell.font = header_font
                            cell.alignment = alignment
                            cell.border = border

                        # Tự động chỉnh độ rộng cột và kẻ bảng cho dữ liệu
                        for i, col in enumerate(df.columns):
                            # Tính độ dài lớn nhất trong cột để chỉnh chiều rộng
                            column_len = df[col].astype(str).str.len().max()
                            column_len = max(column_len, len(col)) + 4
                            worksheet.column_dimensions[get_column_letter(i+1)].width = column_len
                            
                            # Kẻ bảng cho từng ô dữ liệu
                            for row_num in range(2, len(df) + 2):
                                data_cell = worksheet.cell(row=row_num, column=i+1)
                                data_cell.border = border
                                data_cell.alignment = Alignment(horizontal="center")

                    excel_data = buffer.getvalue()
                
                    # 3. Tạo link tải cho Mobile
                    b64 = base64.b64encode(excel_data).decode()
                    href = f'''
                    <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{file_name}" style="text-decoration: none;">
                        <button style="width: 100%; background-color: #28a745; color: white; padding: 15px; border: none; border-radius: 10px; font-weight: bold; font-size: 16px; cursor: pointer;">
                            📥 BẤM VÀO ĐÂY ĐỂ TẢI VỀ
                        </button>
                    </a>
                    '''
                    st.markdown(href, unsafe_allow_html=True)
                    st.success(f"Đã sẵn sàng file: {file_name}")

            with col2:
                # NÚT RESET DỮ LIỆU NGÀY MỚI
                if st.button("🗑️ Reset dữ liệu ngày mới"):
                    # Tạo bảng trống
                    df_reset = pd.DataFrame(columns=["ID", "HoTen", "SDT", "GapAi", "MucDich", "GioVao", "GioRa"])
                    df_reset.to_excel(FILE_NAME, index=False)
                    
                    st.warning("Đã xóa sạch dữ liệu. Đang làm mới hệ thống...")
                    st.balloons()
                    # Tự động load lại trang để bảng trắng tinh
                    st.rerun()
            
            st.info("💡 Lưu ý: Hãy Tải file Excel trước khi bấm Reset để lưu trữ báo cáo nhé!")

    elif password != "":
        if len(password) >= 6:
            st.error("❌ Mật khẩu không chính xác!")
