import streamlit as st
import io
import fitz  # PyMuPDF
from supabase_client import upload_to_supabase
from supabase_table_client import insert_drawing_metadata

BUCKET = "drawings"

st.title("📤 Upload Drawing")

uploaded_file = st.file_uploader("Upload PDF Drawing", type=["pdf"])

# Digit size dropdown
digit_sizes = ["6", "10", "13", "16", "20", "24", "28", "32", "36", "40", "48", "61", "76", "89", "114"]
digit_size = st.selectbox("LED Digit Size (in inches)", digit_sizes)

# Price changer count
changer_count = st.number_input("Price Changer Count", min_value=0, step=1)

# Width inputs
st.markdown("**Width**")
col1, col2 = st.columns(2)
width_ft = col1.number_input("Feet", min_value=0, step=1, key="width_ft")
width_in = col2.number_input("Inches", min_value=0.0, step=0.001, format="%.3f", key="width_in")

# Height inputs
st.markdown("**Height**")
col3, col4 = st.columns(2)
height_ft = col3.number_input("Feet", min_value=0, step=1, key="height_ft")
height_in = col4.number_input("Inches", min_value=0.0, step=0.001, format="%.3f", key="height_in")

# Panel options
st.markdown("**Panels**")
bonfire = st.checkbox("Bonfire Panel")
trv = st.checkbox("Trucks & RVs Panel")
ethanol = st.checkbox("Ethanol-Free Panel")
nitro = st.checkbox("Nitro Panel")

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

            # Construct dimensions and square footage
            width_str = f"{width_ft}ft{width_in:.3f}in"
            height_str = f"{height_ft}ft{height_in:.3f}in"
            square_footage = round((width_ft + width_in / 12) * (height_ft + height_in / 12), 2)

            # Metadata dictionary
            metadata = {
                "file_name": file_name,
                "square_footage": square_footage,
                "digit_size": f"{digit_size}IN",
                "changer_count": changer_count,
                "width": width_str,
                "height": height_str,
                "bonfire": bonfire,
                "trv": trv,
                "ethanol": ethanol,
                "nitro": nitro,
                "supabase_url": supa_url,
                "preview_url": preview_url
            }

            insert_drawing_metadata(metadata)
            st.success("✅ Upload complete and metadata saved.")
            st.image(preview_url, caption="Preview Image", use_container_width=True)

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
