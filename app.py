import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Ghép file giữ nguyên kiểu dữ liệu", layout="wide")

st.title("📂 Ghép file & Giữ nguyên kiểu dữ liệu")

# Upload nhiều file
uploaded_files = st.file_uploader(
    "Chọn nhiều file Excel/CSV", 
    accept_multiple_files=True,
    type=["xlsx", "xls", "csv"]
)

if uploaded_files:
    dataframes = []

    for file in uploaded_files:
        # Xác định kiểu file
        if file.name.endswith(".csv"):
            df = pd.read_csv(file, dtype=str)  # đọc tất cả thành str để không mất thông tin
        else:
            df = pd.read_excel(file, dtype=str)

        # Chuyển lại kiểu dữ liệu nếu muốn
        for col in df.columns:
            # Nếu toàn bộ giá trị trong cột là số => chuyển sang float hoặc int
            if df[col].str.replace('.', '', 1).str.isnumeric().all():
                if df[col].str.contains('.').any():
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                else:
                    df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")

            # Nếu toàn bộ giá trị là ngày => parse datetime
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore", format="%Y-%m-%d")
            except:
                pass

        dataframes.append(df)

    # Ghép các file
    final_df = pd.concat(dataframes, ignore_index=True)

    st.subheader("📊 Dữ liệu đã ghép")
    st.dataframe(final_df)

    # Xuất file giữ nguyên định dạng
    towrite = io.BytesIO()
    final_df.to_excel(towrite, index=False, engine="openpyxl")
    towrite.seek(0)
    st.download_button(
        label="📥 Tải về file Excel",
        data=towrite,
        file_name="file_ghep.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
