import streamlit as st
from pathlib import Path
from supabase_client import upload_to_supabase
from supabase_table_client import insert_drawing_metadata
import fitz  # PyMuPDF
import io

BUCKET = "drawings"
st.set_page_config(page_title="Upload Drawing", layout="wide")
st.title("📤 Upload New Sunshine Drawing")

with st.container():
    # --- Upload Section ---
    uploaded_file = st.file_uploader("Upload PDF Drawing", type=["pdf"])

    # --- Metadata Entry ---
    digit_size = st.selectbox("LED Digit Size", [
        "6", "10", "13", "16", "20", "24", "28", "32", "36", "40", "48", "61", "76", "89", "114"
    ]) + "IN"

    col1, col2 = st.columns(2)
    with col1:
        width_ft = st.text_input("Width (feet)", value="0", key="width_ft")
    with col2:
        width_in = st.text_input("Width (inches)", value="0", key="width_in")

    col3, col4 = st.columns(2)
    with col3:
        height_ft = st.text_input("Height (feet)", value="0", key="height_ft")
    with col4:
        height_in = st.text_input("Height (inches)", value="0", key="height_in")

    # Convert to float
    try:
        total_width = int(width_ft) + float(width_in) / 12
        total_height = int(height_ft) + float(height_in) / 12
        square_footage = round(total_width * total_height, 2)
    except ValueError:
        square_footage = 0.0

    changer_count = st.text_input("Price Changer Count", value="0")

    col5, col6 = st.columns(2)
    with col5:
        bonfire = st.checkbox("Bonfire Panel")
        trv = st.checkbox("Trucks & RVs Panel")
    with col6:
        ethanol = st.checkbox("Ethanol-Free Panel")
        nitro = st.checkbox("Nitro Panel")

    # --- Save File ---
    if uploaded_file and st.button("Save Drawing"):
        width_str = f"{int(width_ft)}ft{float(width_in):.3f}in"
        height_str = f"{int(height_ft)}ft{float(height_in):.3f}in"
        panels = []
        if bonfire: panels.append("BON")
        if trv: panels.append("TRV")
        if ethanol: panels.append("ETH")
        if nitro: panels.append("NITRO")
        panel_str = "-".join(panels)
        file_name = f"{digit_size} {changer_count}P {width_str} x {height_str} {panel_str}".strip()

        file_bytes = uploaded_file.read()
        supa_url = upload_to_supabase(BUCKET, f"{file_name}.pdf", file_bytes)

        # Generate preview thumbnail
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            image_bytes = io.BytesIO(pix.tobytes("png"))
            preview_path = f"{file_name}.png"
            upload_to_supabase(BUCKET, preview_path, image_bytes.getvalue())
        except Exception as e:
            st.error(f"Failed to generate preview: {e}")

        # Insert metadata
        metadata = {
            "File Name": file_name + ".pdf",
            "Square Footage": square_footage,
            "Digit Size": digit_size,
            "Price Changer Count": int(changer_count),
            "Width": width_str,
            "Height": height_str,
            "Bonfire Panel": bonfire,
            "Trucks & RVs Panel": trv,
            "Ethanol-Free Panel": ethanol,
            "Nitro Panel": nitro,
            "Supabase URL": supa_url
        }
        insert_drawing_metadata(metadata)
        st.success("✅ Drawing uploaded and saved to Supabase.")
