import os
import pandas as pd
import streamlit as st
from pdf2image import convert_from_path
from utils.matching import find_best_matches

# Constants
CSV_PATH = "data/drawings.csv"

st.set_page_config(page_title="Sunshine Drawing Lookup", layout="centered")

# Load data
if os.path.exists(CSV_PATH):
    data = pd.read_csv(CSV_PATH)
else:
    st.error("No drawing data found. Please upload files first.")
    st.stop()

st.title("Sunshine Drawing Lookup")

col1, col2 = st.columns(2)
lookup_sqft_input = col1.text_input("Allowed Square Footage")
lookup_changers_input = col2.text_input("Price Changer Count")

lookup_bonfire = st.checkbox("Bonfire Panel", key="lookup_bonfire")
lookup_trv = st.checkbox("Trucks & RV Panel", key="lookup_trv")
lookup_ethanol = st.checkbox("Ethanol-Free Panel", key="lookup_ethanol")
lookup_nitro = st.checkbox("Nitro Panel", key="lookup_nitro")

if st.button("Search Matches"):
    try:
        lookup_sqft = float(lookup_sqft_input)
        lookup_changers = int(lookup_changers_input)

        matches = find_best_matches(data, lookup_sqft, lookup_changers,
                                    lookup_bonfire, lookup_trv,
                                    lookup_ethanol, lookup_nitro)
        if matches.empty:
            st.warning("No matching drawings found.")
        else:
            for _, row in matches.iterrows():
                st.subheader(row["drawing_id"])
                st.write(f"{row['width']}ft x {row['height']}ft • {row['price_changers']}P • {row['digit_size']}")
                st.write(f"Panels: BON: {row['has_bonfire']}, TRV: {row['has_trv']}, ETH: {row['has_ethanol']}, NITRO: {row['has_nitro']}")
                img = convert_from_path(row["file_path"], first_page=1, last_page=1, size=(300, None))[0]
                st.image(img, caption="Preview")
                with open(row["file_path"], "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=os.path.basename(row["file_path"]))
    except ValueError:
        st.error("Please enter valid numbers for square footage and changer count.")
