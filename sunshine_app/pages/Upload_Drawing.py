import streamlit as st
import io
import fitz  # PyMuPDF
from supabase_client import upload_to_supabase
from supabase_table_client import insert_drawing_metadata

BUCKET = "drawings"

st.title("📤 Upload Drawing")

uploaded_file = st.file_uploader("Upload PDF Drawing", type=["pdf"])
if uploaded_file:
    with st.spinner("Uploading and processing..."):
        try:
            # Read PDF bytes
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name

            # Upload PDF to Supabase
            supa_url = upload_to_supabase(BUCKET, file_name, file_bytes)

            # Generate preview image
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            image_bytes = io.BytesIO(pix.tobytes("png"))
            preview_name = file_name.replace(".pdf", ".png")
            preview_url = upload_to_supabase(BUCKET, preview_name, image_bytes.getvalue())

            # Sample metadata (replace with actual form input values in your app)
            metadata = {
                "file_name": file_name,
                "square_footage": 100.0,
                "digit_size": "10IN",
                "changer_count": 3,
                "width": "4ft0in",
                "height": "6ft0in",
                "bonfire": True,
                "trv": False,
                "ethanol": False,
                "nitro": True,
                "supabase_url": supa_url,
                "preview_url": preview_url
            }

            insert_drawing_metadata(metadata)
            st.success("✅ Upload complete and metadata saved.")
            st.image(preview_url, caption="Preview Image", use_container_width=True)

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
