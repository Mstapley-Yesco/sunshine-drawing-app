import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="View Uploaded Drawings", layout="wide")
st.title("📁 View Uploaded Sunshine Drawings")

# Load the CSV database
csv_path = "data/drawings_metadata.csv"
if not Path(csv_path).exists():
    st.warning("No drawings uploaded yet.")
    st.stop()

df = pd.read_csv(csv_path)

# Sort by Digit Size then Price Changer Count
df = df.sort_values(by=["Digit Size", "Price Changer Count"])

for _, row in df.iterrows():
    col1, col2 = st.columns([2, 6])

    with col1:
        st.markdown(f"**File Name:** `{row['File Name']}`")
        st.markdown(f"**Square Footage:** `{row['Square Footage']}`")
        st.markdown(f"**Digit Size:** `{row['Digit Size']}`")
        st.markdown(f"**Changer Count:** `{row['Price Changer Count']}`")
        panels = []
        if row.get("Bonfire Panel"): panels.append("BON")
        if row.get("Trucks & RVs Panel"): panels.append("TRV")
        if row.get("Ethanol-Free Panel"): panels.append("ETH")
        if row.get("Nitro Panel"): panels.append("NITRO")
        st.markdown("**Panels:** " + (", ".join(panels) if panels else "None"))

        st.markdown(f"[⬇️ Download Drawing]({row['Supabase URL']})", unsafe_allow_html=True)

    with col2:
        if pd.notna(row["Supabase URL"]):
            st.image(row["Supabase URL"], width=200)
        else:
            st.warning("No preview available.")

    st.markdown("---")
