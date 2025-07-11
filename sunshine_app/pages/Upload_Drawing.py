import streamlit as st
import pandas as pd
import os
from supabase_client import upload_to_supabase
from datetime import datetime

CSV_PATH = "data/drawings.csv"
BUCKET = "drawings"

st.set_page_config(page_title="Upload Drawing", layout="centered")
st.title("📤 Upload New Drawing")

# Collect form inputs
digit_size = st.selectbox("LED Digit Size (inches)", [
    "6", "10", "13", "16", "20", "24", "28", "32", "36", "40", "48", "61", "76", "89", "114"
])
col1, col2 = st.columns(2)
with col1:
    width_ft = st.number_input("Width (feet)", min_value=0, step=1)
    height_ft = st.number_input("Height (feet)", min_value=0, step=1)
with col2:
    width_in = st.number_input("Width (inches)", min_value=0.0, step=0.125, format="%.3f")
    height_in = st.number_input("Height (inches)", min_value=0.0, step=0.125, format="%.3f")

price_changers = st.text_input("Price Changer Count", value="0")
has_bonfire = st.checkbox("Bonfire Panel")
has_trv = st.checkbox("Trucks & RV Panel")
has_ethanol = st.checkbox("Ethanol-Free Panel")
has_nitro = st.checkbox("Nitro Panel")

uploaded_file = st.file_uploader("Upload PDF Drawing", type="pdf")

# Save entry
if st.button("Upload to Supabase"):
    if not uploaded_file:
        st.error("Please upload a file.")
        st.stop()

    try:
        changers = int(price_changers)
    except:
        st.error("Price changer count must be a number.")
        st.stop()

    # Calculate square footage
    width_total = width_ft + width_in / 12
    height_total = height_ft + height_in / 12
    sq_ft = round(width_total * height_total, 2)

    # Build ID and upload
    panels = []
    if has_bonfire: panels.append("BON")
    if has_trv: panels.append("TRV")
    if has_ethanol: panels.append("ETH")
    if has_nitro: panels.append("NITRO")
    panel_str = "-".join(panels)

    dims = f"{int(width_ft)}ft{int(width_in)}in x {int(height_ft)}ft{int(height_in)}in"
    drawing_id = f"{digit_size}IN {changers}P {dims} {panel_str}".strip()

    file_bytes = uploaded_file.read()
    supa_url = upload_to_supabase(BUCKET, f"{drawing_id}.pdf", file_bytes)

    if not supa_url:
        st.error("Failed to upload to Supabase.")
        st.stop()

    # Save metadata
    new_entry = {
        "drawing_id": drawing_id,
        "digit_size": int(digit_size),
        "price_changers": changers,
        "sq_ft": sq_ft,
        "has_bonfire": has_bonfire,
        "has_trv": has_trv,
        "has_ethanol": has_ethanol,
        "has_nitro": has_nitro,
        "file_path": supa_url
    }

    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = df[df["drawing_id"] != drawing_id]  # remove duplicates
        df = df.append(new_entry, ignore_index=True)
    else:
        df = pd.DataFrame([new_entry])

    df.to_csv(CSV_PATH, index=False)
    st.success(f"Drawing '{drawing_id}' uploaded and saved.")
