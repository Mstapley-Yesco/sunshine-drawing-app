import streamlit as st
from pathlib import Path
from supabase_client import upload_to_supabase
from supabase_table_client import insert_drawing_metadata
import fitz  # PyMuPDF
import io

BUCKET = "drawings"
st.set_page_config(page_title="Upload Drawing", layout="wide")

# Wide margins using columns
left_margin, center_col, right_margin = st.columns([1, 2, 1])

with center_col:
    st.title("📤 Upload New Sunshine Drawing")

    uploaded_file = st.file_uploader("Upload PDF Drawing", type=["pdf"])

    digit_size = st.selectbox("LED Digit Size", [
        "6", "10", "13", "16", "20", "24", "28", "32", "36", "40", "48", "61", "76", "89", "114"
    ]) + "IN"

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        width_ft = st.text_input("Width (feet)", value="0", key="width_ft")
    with col_w2:
        width_in = st.text_input("Width (inches)", value="0", key="width_in")

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        height_ft = st.text_input("Height (feet)", value="0", key="height_ft")
    with col_h2:
        height_in = st.text_input("Height (inches)", value="0", key="height_in")

    try:
        total_width = int(width_ft) + float(width_in) / 12
        total_height = int(height_ft) + float(height_in) / 12
        square_footage = round(total_width * total_height, 2)
    except ValueError:
        square_footage = 0.0

    changer_count = st.text_input("Price Changer Count", value="0")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        bonfire = st.checkbox("Bonfire Panel")
        trv = st.checkbox("Trucks & RVs Panel")
    with col_b2:
        ethanol = st.checkbox("Ethanol-Free Panel")
        nitro = st.checkbox("Nitro Panel")

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

        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            image_bytes = io.BytesIO(pix.tobytes("png"))
            preview_path = f"{file_name}.png"
            upload_to_supabase(BUCKET, preview_path, image_bytes.getvalue())
        except Exception as e:
            st.error(f"Failed to generate preview: {e}")

        metadata = {
            "file_name": f"{file_name}.pdf",
            "square_footage": square_footage,
            "digit_size": digit_size,
            "changer_count": int(changer_count),
            "width": width_str,
            "height": height_str,
            "bonfire": bonfire,
            "trv": trv,
            "ethanol": ethanol,
            "nitro": nitro,
            "supabase_url": supa_url
        }

        try:
            print("📦 Final metadata to upload:")
            print(metadata)
            insert_drawing_metadata(metadata)
            st.success("✅ Drawing uploaded and saved to Supabase.")
        except Exception as e:
            st.error(f"❌ Failed to insert metadata: {e}")
