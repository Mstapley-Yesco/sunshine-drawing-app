import os
import pandas as pd
import streamlit as st
import fitz  # PyMuPDF

CSV_PATH = "data/drawings.csv"

st.set_page_config(page_title="View Files", layout="wide")
st.title("📁 View All Uploaded Drawings")

if not os.path.exists(CSV_PATH):
    st.info("No data found.")
    st.stop()

data = pd.read_csv(CSV_PATH)
data = data.sort_values(by=["digit_size", "price_changers"])

for _, row in data.iterrows():
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"**{row['drawing_id']}**")
        st.markdown(f"- SqFt: {row['sq_ft']}")
        st.markdown(f"- Changers: {row['price_changers']}")
        with open(row["file_path"], "rb") as f:
            st.download_button("⬇ Download", f, file_name=os.path.basename(row["file_path"]))
    with col2:
        try:
            doc = fitz.open(row["file_path"])
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # reduce size
            st.image(pix.tobytes("png"), use_container_width=False)
        except:
            st.write("Preview unavailable.")
