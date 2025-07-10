import os
import pandas as pd
import streamlit as st
import fitz  # PyMuPDF

CSV_PATH = "data/drawings.csv"

st.set_page_config(page_title="View Files", layout="wide")
st.title("📁 View All Uploaded Drawings")

if not os.path.exists(CSV_PATH):
    st.info("No data found.")
    st.stop()

data = pd.read_csv(CSV_PATH)
data = data.sort_values(by=["digit_size", "price_changers"])

if "delete_confirm" not in st.session_state:
    st.session_state.delete_confirm = None

for idx, row in data.iterrows():
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"**{row['drawing_id']}**")
        st.markdown(f"- SqFt: {row['sq_ft']}")
        st.markdown(f"- Changers: {row['price_changers']}")
        with open(row["file_path"], "rb") as f:
            st.download_button("⬇ Download", f, file_name=os.path.basename(row["file_path"]), key=f"download_{idx}")

        # Delete button with confirmation
        if st.session_state.delete_confirm == row["drawing_id"]:
            st.warning(f"Are you sure you want to delete `{row['drawing_id']}`?")
            confirm_col1, confirm_col2 = st.columns(2)
            if confirm_col1.button("✅ Yes, Delete", key=f"confirm_{idx}"):
                try:
                    os.remove(row["file_path"])
                except:
                    pass
                data = data[data["drawing_id"] != row["drawing_id"]]
                data.to_csv(CSV_PATH, index=False)
                st.session_state.delete_confirm = None
                st.rerun()
            if confirm_col2.button("❌ Cancel", key=f"cancel_{idx}"):
                st.session_state.delete_confirm = None
        else:
            if st.button("🗑️ Delete", key=f"delete_{idx}"):
                st.session_state.delete_confirm = row["drawing_id"]

    with col2:
        try:
            doc = fitz.open(row["file_path"])
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
            st.image(pix.tobytes("png"), use_container_width=False)
        except:
            st.write("Preview unavailable.")
