import streamlit as st
import pandas as pd
import os
from supabase_client import upload_to_supabase

CSV_PATH = "data/drawings.csv"
BUCKET = "drawings"

st.set_page_config(page_title="Upload Drawing", layout="centered")
st.title("📤 Upload New Drawing")

# Drag-and-drop first
uploaded_file = st.file_uploader("Upload PDF Drawing", type="pdf")

digit_size = st.selectbox("LED Digit Size (inches)", [
    "6", "10", "13", "16", "20", "24", "28", "32", "36", "40", "48", "61", "76", "89", "114"
])

# Width side-by-side
st.markdown("**Width**")
width_col1, width_col2 = st.columns(2)
with width_col1:
    width_ft = st.text_input("Feet", value="0", key="width_ft")
with width_col2:
    width_in = st.text_input("Inches", value="0.0", key="width_in")

# Height side-by-side
st.markdown("**Height**")
height_col1, height_col2 = st.columns(2)
with height_col1:
    height_ft = st.text_input("Feet", value="0", key="height_ft")
with height_col2:
    height_in = st.text_input("Inches", value="0.0", key="height_in")

price_changers = st.text_input("Price Changer Count", value="0")
has_bonfire = st.checkbox("Bonfire Panel")
has_trv = st.checkbox("Trucks & RV Panel")
has_ethanol = st.checkbox("Ethanol-Free Panel")
has_nitro = st.checkbox("Nitro Panel")

# Save entry
if st.button("Upload to Database"):
    if not uploaded_file:
        st.error("Please upload a file.")
        st.stop()

    try:
        changers = int(price_changers)
        width_total = float(width_ft) + float(width_in) / 12
        height_total = float(height_ft) + float(height_in) / 12
    except:
        st.error("Width, height, and price changer count must be numeric.")
        st.stop()

    sq_ft = round(width_total * height_total, 2)

    panels = []
    if has_bonfire: panels.append("BON")
    if has_trv: panels.append("TRV")
    if has_ethanol: panels.append("ETH")
    if has_nitro: panels.append("NITRO")
    panel_str = "-".join(panels)

    dims = f"{int(float(width_ft))}ft{int(float(width_in))}in x {int(float(height_ft))}ft{int(float(height_in))}in"
    drawing_id = f"{digit_size}IN {changers}P {dims} {panel_str}".strip()

    file_bytes = uploaded_file.read()
    supa_url = upload_to_supabase(BUCKET, f"{drawing_id}.pdf", file_bytes)

    if not supa_url:
        st.error("Failed to upload.")
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
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([new_entry])

    df.to_csv(CSV_PATH, index=False)
    st.success(f"Drawing '{drawing_id}' uploaded and saved.")
