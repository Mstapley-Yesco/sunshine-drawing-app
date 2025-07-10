import os
import pandas as pd
import streamlit as st
import fitz  # PyMuPDF

# Constants
DRAWINGS_DIR = "data/drawings"
CSV_PATH = "data/drawings.csv"
DIGIT_SIZES = [
    '6"', '10"', '13"', '16"', '20"', '24"', '28"', '32"',
    '36"', '40"', '48"', '61"', '76"', '89"', '114"'
]

os.makedirs(DRAWINGS_DIR, exist_ok=True)
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=[
        "drawing_id", "digit_size", "width", "height", "sq_ft", "price_changers",
        "has_bonfire", "has_trv", "has_ethanol", "has_nitro", "file_path"
    ]).to_csv(CSV_PATH, index=False)

data = pd.read_csv(CSV_PATH)

st.set_page_config(page_title="Upload Drawing", layout="centered")
st.title("📤 Upload Drawing")

# --- Reset logic BEFORE rendering widgets ---
if st.session_state.get("reset_form"):
    for key in ["width_ft", "width_in", "height_ft", "height_in", "changer_count"]:
        st.session_state[key] = "0"
    for key in ["has_bonfire", "has_trv", "has_ethanol", "has_nitro"]:
        st.session_state[key] = False
    st.session_state["digit_size"] = '10"'
    st.session_state["reset_form"] = False
    st.rerun()

# --- Upload form ---
with st.form("upload_form"):
    uploaded_file = st.file_uploader("Upload PDF Drawing", type=["pdf"], key="file")
    digit_size = st.selectbox("LED Digit Size (inches)", DIGIT_SIZES, key="digit_size")

    w_col1, w_col2 = st.columns(2)
    width_feet = w_col1.text_input("Width - Feet", key="width_ft")
    width_inches = w_col2.text_input("Width - Inches", key="width_in")

    h_col1, h_col2 = st.columns(2)
    height_feet = h_col1.text_input("Height - Feet", key="height_ft")
    height_inches = h_col2.text_input("Height - Inches", key="height_in")

    changer_input = st.text_input("Price Changer Count", key="changer_count")
    has_bonfire = st.checkbox("Bonfire Panel", key="has_bonfire")
    has_trv = st.checkbox("Trucks & RV Panel", key="has_trv")
    has_ethanol = st.checkbox("Ethanol-Free Panel", key="has_ethanol")
    has_nitro = st.checkbox("Nitro Panel", key="has_nitro")

    submit = st.form_submit_button("Save Drawing")

def convert_feet_inches(feet_str, inches_str):
    feet = float(feet_str.strip()) if feet_str.strip() else 0.0
    inches = float(inches_str.strip()) if inches_str.strip() else 0.0
    return round(feet + (inches / 12), 5)

def format_dimension(feet_str, inches_str):
    ft = int(float(feet_str.strip()))
    inch = float(inches_str.strip())
    if inch.is_integer(): inch = int(inch)
    return f"{ft}ft{inch}in"

if submit and uploaded_file:
    try:
        width = convert_feet_inches(width_feet, width_inches)
        height = convert_feet_inches(height_feet, height_inches)
        sq_ft = round(width * height, 2)
        price_changers = int(changer_input)
    except Exception as e:
        st.error("Invalid dimensions or price changer count.")
        st.stop()

    panels = []
    if has_bonfire: panels.append("BON")
    if has_trv: panels.append("TRV")
    if has_ethanol: panels.append("ETH")
    if has_nitro: panels.append("NITRO")
    panel_str = "-".join(panels)
    digit_label = digit_size.replace('"', '') + "IN"
    width_label = format_dimension(width_feet, width_inches)
    height_label = format_dimension(height_feet, height_inches)
    filename = f"{digit_label} {price_changers}P {width_label} x {height_label} {panel_str}.pdf"
    path = os.path.join(DRAWINGS_DIR, filename)
    drawing_id = os.path.splitext(filename)[0]

    if os.path.exists(path):
        st.warning("⚠️ A drawing with this name already exists.")
        try:
            doc = fitz.open(path)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            st.image(pix.tobytes("png"), caption="Existing Drawing Preview", use_container_width=True)
        except Exception as e:
            st.error("Preview not available.")
        st.markdown(f"**Existing file:** `{filename}`")
        if st.button("✅ Overwrite Existing"):
            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            data = data[data["drawing_id"] != drawing_id]
    else:
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    new_row = {
        "drawing_id": drawing_id, "digit_size": digit_size,
        "width": width, "height": height, "sq_ft": sq_ft,
        "price_changers": price_changers,
        "has_bonfire": has_bonfire, "has_trv": has_trv,
        "has_ethanol": has_ethanol, "has_nitro": has_nitro,
        "file_path": path
    }
    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
    data.to_csv(CSV_PATH, index=False)
    st.success(f"✅ Saved: {filename}")

# --- Clear & Refresh Button ---
if st.button("🔄 Clear Form and Refresh"):
    st.session_state["reset_form"] = True
    st.rerun()
