import os
import pandas as pd
import streamlit as st
import fitz  # PyMuPDF

CSV_PATH = "data/drawings.csv"

st.set_page_config(page_title="Sunshine Drawing Lookup", layout="wide")
st.title("Sunshine Drawing Lookup")

if not os.path.exists(CSV_PATH):
    st.warning("No drawings found. Please upload drawings first.")
    st.stop()

data = pd.read_csv(CSV_PATH)

col1, col2 = st.columns(2)
with col1:
    sqft = st.text_input("Allowed Square Footage")
with col2:
    price_changers = st.text_input("Price Changer Count")

has_bonfire = st.checkbox("Bonfire Panel")
has_trv = st.checkbox("Trucks & RV Panel")
has_ethanol = st.checkbox("Ethanol-Free Panel")
has_nitro = st.checkbox("Nitro Panel")

def compute_match_score(row, sqft_val, changers):
    score = 0
    if sqft_val > 0:
        score += abs(row["sq_ft"] - sqft_val)
    if changers >= 0:
        score += abs(row["price_changers"] - changers) * 10
    return score

if st.button("Search Matches"):
    try:
        sqft_val = float(sqft)
        changers = int(price_changers)
    except:
        st.error("Please enter valid numbers.")
        st.stop()

    filtered = data.copy()
    if has_bonfire:
        filtered = filtered[filtered["has_bonfire"] == True]
    if has_trv:
        filtered = filtered[filtered["has_trv"] == True]
    if has_ethanol:
        filtered = filtered[filtered["has_ethanol"] == True]
    if has_nitro:
        filtered = filtered[filtered["has_nitro"] == True]

    if filtered.empty:
        st.info("No matching drawings found.")
        st.stop()

    filtered["match_score"] = filtered.apply(lambda row: compute_match_score(row, sqft_val, changers), axis=1)
    results = filtered.sort_values(by="match_score").head(3)

    for _, row in results.iterrows():
        st.markdown(f"### {row['drawing_id']}")
        st.markdown(f"**Square Footage:** {row['sq_ft']} | **Changers:** {row['price_changers']}")
        try:
            doc = fitz.open(row["file_path"])
            page = doc.load_page(0)
            pix = page.get_pixmap()
            st.image(pix.tobytes("png"), use_container_width=True)
        except:
            st.warning("Preview not available.")
