import streamlit as st
import pandas as pd

CSV_PATH = "data/drawings.csv"

st.set_page_config(page_title="View Files", layout="centered")
st.title("📂 All Uploaded Drawings")

if not st.button("Refresh"):
    st.write("")

if not CSV_PATH or not st.session_state.get("loaded_csv", False):
    try:
        df = pd.read_csv(CSV_PATH)
        df["digit_size"] = pd.to_numeric(df["digit_size"])
        df["price_changers"] = pd.to_numeric(df["price_changers"])
        df = df.sort_values(by=["digit_size", "price_changers"])
        st.session_state["df"] = df
        st.session_state["loaded_csv"] = True
    except:
        st.warning("No drawing data available.")
        st.stop()
else:
    df = st.session_state["df"]

for idx, row in df.iterrows():
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Name:** {row['drawing_id']}")
        st.markdown(f"**Size:** {row['sq_ft']} sq ft")
    with col2:
        st.markdown(f"[⬇ Download]({row['file_path']})", unsafe_allow_html=True)
        st.image(row['file_path'], width=150)
