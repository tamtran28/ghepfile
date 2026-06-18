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
    page_title="Công cụ ghép file Excel/CSV",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Công cụ ghép file Excel/CSV")


# =========================================================
# HÀM ĐỌC FILE CSV
# =========================================================
def read_csv_file(uploaded_file):
    """
    Đọc file CSV bằng nhiều bảng mã khác nhau.
    Toàn bộ dữ liệu được đọc dưới dạng chuỗi.
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
        f"Lỗi: {last_error}"
    )


# =========================================================
# HÀM ĐỌC FILE EXCEL
# =========================================================
def read_excel_file(uploaded_file):
    """
    Đọc sheet đầu tiên của file Excel.
    """
    return pd.read_excel(
        uploaded_file,
        sheet_name=0,
        dtype=str,
        keep_default_na=False
    )


# =========================================================
# HÀM ĐỌC FILE CHUNG
# =========================================================
def read_uploaded_file(uploaded_file):
    file_extension = Path(uploaded_file.name).suffix.lower()

    if file_extension == ".csv":
        df = read_csv_file(uploaded_file)
    else:
        df = read_excel_file(uploaded_file)

    # Xóa khoảng trắng thừa trong tên cột
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


# =========================================================
# HÀM CHUYỂN DATAFRAME THÀNH FILE EXCEL
# =========================================================
def dataframe_to_excel(dataframe, sheet_name="Du_lieu_ghep"):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name
        )

        worksheet = writer.sheets[sheet_name]

        # Cố định dòng tiêu đề
        worksheet.freeze_panes = "A2"

        # Bật bộ lọc
        if worksheet.max_row >= 1 and worksheet.max_column >= 1:
            worksheet.auto_filter.ref = worksheet.dimensions

        # Điều chỉnh độ rộng cột
        for column_cells in worksheet.columns:
            column_letter = column_cells[0].column_letter
            max_length = 0

            for cell in column_cells:
                if cell.value is not None:
                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )

            worksheet.column_dimensions[column_letter].width = min(
                max(max_length + 2, 12),
                50
            )

    output.seek(0)
    return output.getvalue()


# =========================================================
# CHỌN CHỨC NĂNG
# =========================================================
st.subheader("Chọn chức năng")

selected_mode = st.radio(
    label="Bạn muốn thực hiện theo cách nào?",
    options=[
        "1. Ghép file giữ nguyên",
        "2. Ghép file nâng cao"
    ],
    horizontal=True
)

if selected_mode == "1. Ghép file giữ nguyên":
    st.info(
        "Chức năng này chỉ ghép dữ liệu từ nhiều file và tải xuống. "
        "Không thêm cột file nguồn và không chỉnh sửa trực tiếp."
    )

else:
    st.info(
        "Chức năng này sẽ thêm cột FILE_NGUON và cho phép "
        "chỉnh sửa, thêm hoặc xóa dòng trước khi tải xuống."
    )


# =========================================================
# UPLOAD FILE
# =========================================================
uploaded_files = st.file_uploader(
    "Chọn nhiều file Excel hoặc CSV",
    accept_multiple_files=True,
    type=["xlsx", "xls", "csv"]
)


# =========================================================
# XỬ LÝ FILE
# =========================================================
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

            df = read_uploaded_file(uploaded_file)

            # Chỉ nhánh nâng cao mới thêm tên file nguồn
            if selected_mode == "2. Ghép file nâng cao":
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
    # HIỂN THỊ FILE LỖI
    # =====================================================
    if error_files:
        st.warning("Một số file không thể đọc được:")

        st.dataframe(
            pd.DataFrame(error_files),
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # GHÉP FILE
    # =====================================================
    if dataframes:
        final_df = pd.concat(
            dataframes,
            ignore_index=True,
            sort=False
        )

        final_df = final_df.fillna("")

        st.success(
            f"Đã ghép thành công **{len(dataframes)} file** – "
            f"tổng cộng **{len(final_df):,} dòng** và "
            f"**{len(final_df.columns):,} cột**."
        )

        # =================================================
        # NHÁNH 1: GHÉP FILE GIỮ NGUYÊN
        # =================================================
        if selected_mode == "1. Ghép file giữ nguyên":
            st.subheader("📊 Dữ liệu đã ghép")

            st.dataframe(
                final_df,
                use_container_width=True,
                hide_index=True,
                height=600
            )

            excel_data = dataframe_to_excel(
                final_df,
                sheet_name="Du_lieu_ghep"
            )

            st.download_button(
                label="📥 Tải file Excel đã ghép",
                data=excel_data,
                file_name="file_ghep_giu_nguyen.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )

        # =================================================
        # NHÁNH 2: THÊM FILE NGUỒN + CHỈNH SỬA
        # =================================================
        else:
            st.subheader("📊 Thống kê dữ liệu theo file nguồn")

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

            st.subheader("✏️ Chỉnh sửa dữ liệu")

            st.caption(
                "Nhấp đúp vào ô để sửa dữ liệu. "
                "Có thể thêm dòng mới hoặc chọn dòng để xóa."
            )

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

            edited_df = edited_df.fillna("")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Số file",
                len(dataframes)
            )

            col2.metric(
                "Số dòng ban đầu",
                f"{len(final_df):,}"
            )

            col3.metric(
                "Số dòng sau chỉnh sửa",
                f"{len(edited_df):,}"
            )

            excel_data = dataframe_to_excel(
                edited_df,
                sheet_name="Du_lieu_da_chinh_sua"
            )

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
