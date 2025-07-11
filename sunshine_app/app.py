import streamlit as st
import pandas as pd
import os

CSV_PATH = "data/drawings.csv"

st.set_page_config(page_title="Sunshine Drawing Lookup", layout="centered")
st.title("Sunshine Drawing Lookup")

col1, col2 = st.columns(2)
with col1:
    allowed_sqft = st.text_input("Allowed Square Footage")
with col2:
    changer_count = st.text_input("Price Changer Count")

# Centered checkboxes
col3, col4 = st.columns(2)
with col3:
    has_bonfire = st.checkbox("Bonfire Panel")
    has_trv = st.checkbox("Trucks & RV Panel")
    has_ethanol = st.checkbox("Ethanol-Free Panel")
    has_nitro = st.checkbox("Nitro Panel")

# Button to trigger match
if st.button("Search Matches"):
    if not allowed_sqft or not changer_count:
        st.warning("Enter square footage and changer count to begin.")
        st.stop()

    try:
        sqft_target = float(allowed_sqft)
        changer_target = int(changer_count)
    except:
        st.error("Invalid input. Please enter numeric values.")
        st.stop()

    if not os.path.exists(CSV_PATH):
        st.error("No drawing data available.")
        st.stop()

    df = pd.read_csv(CSV_PATH)

    df["score"] = (
        abs(df["sq_ft"] - sqft_target) +
        10 * abs(df["price_changers"] - changer_target) +
        5 * (df["has_bonfire"] != has_bonfire) +
        5 * (df["has_trv"] != has_trv) +
        5 * (df["has_ethanol"] != has_ethanol) +
        5 * (df["has_nitro"] != has_nitro)
    )

    top_matches = df.sort_values("score").head(3)

    st.markdown("### Matching Drawings")
    for idx, row in top_matches.iterrows():
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Name:** {row['drawing_id']}")
            st.markdown(f"**Size:** {row['sq_ft']} sq ft")
            st.markdown(f"[⬇ Download]({row['file_path']})", unsafe_allow_html=True)
        with col2:
            st.image(row['file_path'], width=150)
