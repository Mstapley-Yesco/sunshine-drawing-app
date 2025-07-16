import streamlit as st
import io
import fitz
import re
import urllib.parse
from supabase_client import upload_to_supabase, SUPABASE_URL
from supabase_table_client import insert_drawing_metadata, get_all_drawings

BUCKET = "drawings"

def sanitize_filename(name: str) -> str:
    return re.sub(r"[\\s/]+", "_", name)

def encode_url(file_name: str) -> str:
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{urllib.parse.quote(file_name)}"

st.title("📤 Upload Drawing")

uploaded_file = st.file_uploader("Upload PDF Drawing", type=["pdf"])

digit_sizes = ["6", "10", "13", "16", "20", "24", "28", "32", "36", "40", "48", "61", "76", "89", "114"]
digit_size = st.selectbox("LED Digit Size (in inches)", digit_sizes)

changer_count = st.text_input("Price Changer Count", key="changer_count")

st.markdown("**Width**")
col_w1, col_w2 = st.columns(2)
width_ft = col_w1.text_input("Feet", key="width_ft")
width_in = col_w2.text_input("Inches (e.g. 6.125)", key="width_in")

st.markdown("**Height**")
col_h1, col_h2 = st.columns(2)
height_ft = col_h1.text_input("Feet", key="height_ft")
height_in = col_h2.text_input("Inches (e.g. 6.125)", key="height_in")

st.markdown("**Panels**")
bonfire = st.checkbox("Bonfire Panel")
trv = st.checkbox("Trucks & RVs Panel")
ethanol = st.checkbox("Ethanol-Free Panel")
nitro = st.checkbox("Nitro Panel")

show_confirm = False

if uploaded_file:
    original_file_name = uploaded_file.name
    sanitized_file_name = sanitize_filename(original_file_name)

    width_ft = width_ft or "0"
    width_in = width_in or "0"
    height_ft = height_ft or "0"
    height_in = height_in or "0"

    width_str = f"{width_ft}ft{width_in}in"
    height_str = f"{height_ft}ft{height_in}in"

    try:
        width_total = float(width_ft) + float(width_in) / 12
        height_total = float(height_ft) + float(height_in) / 12
        square_footage = round(width_total * height_total, 2)
    except:
        square_footage = 0.0

    # Build current metadata
    current_metadata = {
        "digit_size": f"{digit_size}IN",
        "changer_count": int(changer_count) if changer_count.isdigit() else 0,
        "width": width_str,
        "height": height_str,
        "bonfire": bonfire,
        "trv": trv,
        "ethanol": ethanol,
        "nitro": nitro,
    }

    # Check Supabase for duplicates
    drawings = get_all_drawings()
    duplicate = None
    for d in drawings:
        if all(d.get(k) == v for k, v in current_metadata.items()):
            duplicate = d
            break

    if duplicate:
        st.warning("A drawing with this exact metadata already exists:")
        if duplicate.get("preview_url"):
            st.image(duplicate["preview_url"], caption="Existing Drawing Preview", use_container_width=True)
        confirm = st.checkbox("I confirm I still want to upload this duplicate.")
        show_confirm = confirm
    else:
        show_confirm = True

if uploaded_file and show_confirm and st.button("Upload Drawing"):
    with st.spinner("Uploading and processing..."):
        try:
            file_bytes = uploaded_file.read()
            if not file_bytes:
                st.error("No file content found. Please re-upload your file.")
                st.stop()

            # Upload PDF
            upload_to_supabase(BUCKET, sanitized_file_name, file_bytes)
            supa_url = encode_url(sanitized_file_name)

            # Generate preview
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            matrix = fitz.Matrix(2, 2)
            pix = doc.load_page(0).get_pixmap(matrix=matrix)
            image_bytes = io.BytesIO(pix.tobytes("png"))
            image_bytes.seek(0)
            preview_name = sanitized_file_name.replace(".pdf", ".png")
            upload_to_supabase(BUCKET, preview_name, image_bytes.read())
            preview_url = encode_url(preview_name)

            # Final metadata insert
            metadata = {
                **current_metadata,
                "file_name": original_file_name,
                "square_footage": square_footage,
                "supabase_url": supa_url,
                "preview_url": preview_url
            }

            insert_drawing_metadata(metadata)
            st.success("✅ Upload complete and metadata saved.")
            st.image(preview_url, caption="New Preview", use_container_width=True)

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")