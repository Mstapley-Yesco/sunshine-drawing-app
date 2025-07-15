import streamlit as st
import io
import fitz  # PyMuPDF
from supabase_client import upload_to_supabase
from supabase_table_client import insert_drawing_metadata

BUCKET = "drawings"

st.title("📤 Upload Drawing")

st.markdown("### Upload File")
uploaded_file = st.file_uploader("Upload PDF Drawing", type=["pdf"])

st.write("🖼️ Preview upload result:", preview_response)

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

if uploaded_file and st.button("Upload Drawing"):
    with st.spinner("Uploading and processing..."):
        try:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name

            if not file_bytes:
                st.error("No file content found. Please re-upload your file.")
                st.stop()

            # Upload PDF
            pdf_response = upload_to_supabase(BUCKET, file_name, file_bytes)
            supa_url = pdf_response

            # Generate preview
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            image_bytes = io.BytesIO(pix.tobytes("png"))
            preview_name = file_name.replace(".pdf", ".png")
            preview_response = upload_to_supabase(BUCKET, preview_name, image_bytes.getvalue())
            preview_url = preview_response

            # Default zero-fill
            width_ft = width_ft or "0"
            width_in = width_in or "0"
            height_ft = height_ft or "0"
            height_in = height_in or "0"

            # Format and calculate
            width_str = f"{width_ft}ft{width_in}in"
            height_str = f"{height_ft}ft{height_in}in"
            try:
                width_total = float(width_ft or 0) + float(width_in or 0) / 12
                height_total = float(height_ft or 0) + float(height_in or 0) / 12
                square_footage = round(width_total * height_total, 2)
            except:
                square_footage = 0.0

            # Metadata
            metadata = {
                "file_name": file_name,
                "square_footage": square_footage,
                "digit_size": f"{digit_size}IN",
                "changer_count": int(changer_count) if changer_count.isdigit() else 0,
                "width": width_str,
                "height": height_str,
                "bonfire": bonfire,
                "trv": trv,
                "ethanol": ethanol,
                "nitro": nitro,
                "supabase_url": supa_url,
                "preview_url": preview_url  # ✅ this line ensures preview is stored
            }

            insert_drawing_metadata(metadata)
            st.success("✅ Upload complete and metadata saved.")
            if preview_url:
                st.image(preview_url, caption="Preview Image", use_container_width=True)

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
