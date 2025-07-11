import streamlit as st
from ..supabase_table_client import get_all_drawings

st.set_page_config(page_title="View Uploaded Drawings", layout="wide")
st.title("📁 View Uploaded Sunshine Drawings")

drawings = get_all_drawings()

if not drawings:
    st.warning("No drawings available.")
    st.stop()

# Sort by Digit Size then Price Changer Count
def sort_key(d):
    return (int(d["Digit Size"].replace("IN", "")), d["Price Changer Count"])

drawings.sort(key=sort_key)

for row in drawings:
    col1, col2 = st.columns([2, 6])

    with col1:
        st.markdown(f"**File Name:** `{row['File Name']}`")
        st.markdown(f"**Square Footage:** `{row['Square Footage']}`")
        st.markdown(f"**Digit Size:** `{row['Digit Size']}`")
        st.markdown(f"**Changer Count:** `{row['Price Changer Count']}`")
        st.markdown(f"**Width:** `{row['Width']}`")
        st.markdown(f"**Height:** `{row['Height']}`")
        panels = []
        if row.get("Bonfire Panel"): panels.append("BON")
        if row.get("Trucks & RVs Panel"): panels.append("TRV")
        if row.get("Ethanol-Free Panel"): panels.append("ETH")
        if row.get("Nitro Panel"): panels.append("NITRO")
        st.markdown("**Panels:** " + (", ".join(panels) if panels else "None"))
        st.markdown(f"[⬇️ Download Drawing]({row['Supabase URL']})", unsafe_allow_html=True)

    with col2:
        preview_url = row["Supabase URL"].replace(".pdf", ".png")
        st.image(preview_url, width=200)
    st.markdown("---")
