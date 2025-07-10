import os
import pandas as pd
import streamlit as st
from pdf2image import convert_from_path

st.set_page_config(page_title="View Uploaded Drawings", layout="wide")
st.title("📁 Uploaded Drawings")

CSV_PATH = "data/drawings.csv"

if not os.path.exists(CSV_PATH):
    st.warning("No drawing data found.")
    st.stop()

data = pd.read_csv(CSV_PATH)

def parse_digit_size(digit_str):
    try:
        return int(digit_str.replace('"', ''))
    except:
        return 0

if not data.empty:
    data["digit_numeric"] = data["digit_size"].apply(parse_digit_size)
    data = data.sort_values(by=["digit_numeric", "price_changers"])

    for _, row in data.iterrows():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{row['drawing_id']}**")
            st.markdown(f"📐 **{row['sq_ft']} sq ft**")
            with open(row["file_path"], "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name=os.path.basename(row["file_path"]))
        with col2:
            try:
                img = convert_from_path(row["file_path"], first_page=1, last_page=1, size=(150, None))[0]
                st.image(img, use_container_width=False)
            except Exception as e:
                st.error(f"Could not preview: {e}")
        st.markdown("---")
else:
    st.info("No drawings uploaded yet.")
