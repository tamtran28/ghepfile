# import streamlit as st
# import pandas as pd
# import io

# st.set_page_config(page_title="Ghép file giữ nguyên kiểu dữ liệu", layout="wide")

# st.title("📂 Ghép file & Giữ nguyên kiểu dữ liệu")

# # Upload nhiều file
# uploaded_files = st.file_uploader(
#     "Chọn nhiều file Excel/CSV", 
#     accept_multiple_files=True,
#     type=["xlsx", "xls", "csv"]
# )

# if uploaded_files:
#     dataframes = []

#     for file in uploaded_files:
#         # Xác định kiểu file
#         if file.name.endswith(".csv"):
#             df = pd.read_csv(file, dtype=str)  # đọc tất cả thành str để không mất thông tin
#         else:
#             df = pd.read_excel(file, dtype=str)

#         # Chuyển lại kiểu dữ liệu nếu muốn
#         for col in df.columns:
#             # Nếu toàn bộ giá trị trong cột là số => chuyển sang float hoặc int
#             if df[col].str.replace('.', '', 1).str.isnumeric().all():
#                 if df[col].str.contains('.').any():
#                     df[col] = pd.to_numeric(df[col], errors="coerce")
#                 else:
#                     df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")

#             # Nếu toàn bộ giá trị là ngày => parse datetime
#             try:
#                 df[col] = pd.to_datetime(df[col], errors="ignore", format="%Y-%m-%d")
#             except:
#                 pass

#         dataframes.append(df)

#     # Ghép các file
#     final_df = pd.concat(dataframes, ignore_index=True)

#     st.subheader("📊 Dữ liệu đã ghép")
#     st.dataframe(final_df)

#     # Xuất file giữ nguyên định dạng
#     towrite = io.BytesIO()
#     final_df.to_excel(towrite, index=False, engine="openpyxl")
#     towrite.seek(0)
#     st.download_button(
#         label="📥 Tải về file Excel",
#         data=towrite,
#         file_name="file_ghep.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

import streamlit as st
import pandas as pd
import io
from pathlib import Path

# =========================================================
# CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="Ghép file và chỉnh sửa dữ liệu",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Ghép file và chỉnh sửa dữ liệu")
st.caption(
    "Tải nhiều file Excel/CSV, ghép dữ liệu, chỉnh sửa trực tiếp "
    "và tải kết quả xuống."
)


# =========================================================
# HÀM ĐỌC FILE CSV
# =========================================================
def read_csv_file(uploaded_file):
    """
    Đọc CSV với một số bảng mã thường gặp.
    Toàn bộ dữ liệu được đọc dạng chuỗi để tránh mất số 0 đầu.
    """
    file_bytes = uploaded_file.getvalue()

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1258",
        "latin1"
    ]

    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(
                io.BytesIO(file_bytes),
                dtype=str,
                encoding=encoding,
                keep_default_na=False
            )
        except Exception as error:
            last_error = error

    raise ValueError(
        f"Không thể đọc file CSV {uploaded_file.name}. "
        f"Lỗi cuối cùng: {last_error}"
    )


# =========================================================
# HÀM ĐỌC FILE EXCEL
# =========================================================
def read_excel_file(uploaded_file):
    """
    Đọc sheet đầu tiên của file Excel.
    Dữ liệu được đọc dạng chuỗi để giữ nguyên mã và số 0 đầu.
    """
    return pd.read_excel(
        uploaded_file,
        sheet_name=0,
        dtype=str,
        keep_default_na=False
    )


# =========================================================
# HÀM XUẤT EXCEL
# =========================================================
def dataframe_to_excel(dataframe):
    """
    Chuyển DataFrame thành file Excel trong bộ nhớ.
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Du_lieu_ghep"
        )

        worksheet = writer.sheets["Du_lieu_ghep"]

        # Cố định dòng tiêu đề
        worksheet.freeze_panes = "A2"

        # Bật bộ lọc
        if worksheet.max_row >= 1 and worksheet.max_column >= 1:
            worksheet.auto_filter.ref = worksheet.dimensions

        # Điều chỉnh độ rộng cột
        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:
                if cell.value is not None:
                    cell_length = len(str(cell.value))
                    max_length = max(max_length, cell_length)

            worksheet.column_dimensions[column_letter].width = min(
                max(max_length + 2, 12),
                50
            )

    output.seek(0)
    return output.getvalue()


# =========================================================
# UPLOAD FILE
# =========================================================
uploaded_files = st.file_uploader(
    "Chọn nhiều file Excel hoặc CSV",
    accept_multiple_files=True,
    type=["xlsx", "xls", "csv"]
)

if uploaded_files:
    dataframes = []
    error_files = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for index, uploaded_file in enumerate(uploaded_files):
        try:
            status_text.write(
                f"Đang xử lý: **{uploaded_file.name}**"
            )

            file_extension = Path(uploaded_file.name).suffix.lower()

            if file_extension == ".csv":
                df = read_csv_file(uploaded_file)
            else:
                df = read_excel_file(uploaded_file)

            # Chuẩn hóa tên cột
            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            # Thêm cột tên file nguồn ở vị trí đầu tiên
            df.insert(
                0,
                "FILE_NGUON",
                uploaded_file.name
            )

            dataframes.append(df)

        except Exception as error:
            error_files.append(
                {
                    "Tên file": uploaded_file.name,
                    "Lỗi": str(error)
                }
            )

        progress_bar.progress(
            (index + 1) / len(uploaded_files)
        )

    progress_bar.empty()
    status_text.empty()

    # =====================================================
    # HIỂN THỊ FILE BỊ LỖI
    # =====================================================
    if error_files:
        st.warning("Một số file không thể đọc được:")

        st.dataframe(
            pd.DataFrame(error_files),
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # GHÉP DỮ LIỆU
    # =====================================================
    if dataframes:
        final_df = pd.concat(
            dataframes,
            ignore_index=True,
            sort=False
        )

        # Thay NaN phát sinh do các file không giống cột nhau
        final_df = final_df.fillna("")

        st.success(
            f"Đã đọc thành công **{len(dataframes)} file** – "
            f"tổng cộng **{len(final_df):,} dòng** và "
            f"**{len(final_df.columns):,} cột**."
        )

        # =================================================
        # THỐNG KÊ THEO FILE NGUỒN
        # =================================================
        with st.expander("📊 Xem số lượng dòng theo từng file"):
            file_summary = (
                final_df["FILE_NGUON"]
                .value_counts(dropna=False)
                .rename_axis("Tên file")
                .reset_index(name="Số dòng")
            )

            st.dataframe(
                file_summary,
                use_container_width=True,
                hide_index=True
            )

        st.subheader("✏️ Chỉnh sửa dữ liệu trước khi tải xuống")

        st.info(
            "Bạn có thể nhấp đúp vào ô để sửa, sao chép dữ liệu từ Excel "
            "để dán vào bảng, thêm dòng mới hoặc chọn dòng để xóa."
        )

        # =================================================
        # BẢNG CHỈNH SỬA
        # =================================================
        edited_df = st.data_editor(
            final_df,
            key="data_editor_ghep_file",
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            height=600,
            column_config={
                "FILE_NGUON": st.column_config.TextColumn(
                    "File nguồn",
                    help="Tên file chứa dòng dữ liệu ban đầu",
                    width="medium"
                )
            }
        )

        # Chuẩn hóa lại dữ liệu sau chỉnh sửa
        edited_df = edited_df.fillna("")

        st.write(
            f"Dữ liệu sau chỉnh sửa: **{len(edited_df):,} dòng** – "
            f"**{len(edited_df.columns):,} cột**."
        )

        # =================================================
        # XUẤT FILE
        # =================================================
        excel_data = dataframe_to_excel(edited_df)

        st.download_button(
            label="📥 Tải file Excel sau khi chỉnh sửa",
            data=excel_data,
            file_name="file_ghep_da_chinh_sua.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True
        )

else:
    st.info("Vui lòng tải lên ít nhất một file Excel hoặc CSV.")
