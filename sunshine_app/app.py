import streamlit as st
import pandas as pd

CSV_PATH = "data/drawings.csv"

st.set_page_config(page_title="Sunshine Drawing Lookup", layout="centered")
st.title("Sunshine Drawing Lookup")

# Sidebar Inputs
col1, col2 = st.columns(2)
with col1:
    allowed_sqft = st.text_input("Allowed Square Footage")
with col2:
    changer_count = st.text_input("Price Changer Count")

has_bonfire = st.sidebar.checkbox("Bonfire Panel")
has_trv = st.sidebar.checkbox("Trucks & RV Panel")
has_ethanol = st.sidebar.checkbox("Ethanol-Free Panel")
has_nitro = st.sidebar.checkbox("Nitro Panel")

# Load Data
if not allowed_sqft or not changer_count:
    st.warning("Enter square footage and changer count to begin.")
    st.stop()

try:
    sqft_target = float(allowed_sqft)
    changer_target = int(changer_count)
except:
    st.error("Invalid input. Please enter numeric values.")
    st.stop()

if not CSV_PATH or not os.path.exists(CSV_PATH):
    st.error("No drawing data available.")
    st.stop()

df = pd.read_csv(CSV_PATH)

# Matching logic (simplified)
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
