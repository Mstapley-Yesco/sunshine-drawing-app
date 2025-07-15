import streamlit as st
import pandas as pd
import requests
from supabase_table_client import get_all_drawings

st.set_page_config(layout="wide")

# Three-column layout for consistent margins
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("Sunshine Drawing Lookup")

    # Load data from Supabase
    drawings = get_all_drawings()
    if not drawings:
        st.error("No drawing data available.")
        st.stop()

    df = pd.DataFrame(drawings)

    # Ensure numeric fields are valid
    for field in ["square_footage", "changer_count"]:
        df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

    st.subheader("Search Criteria")
    square_footage = st.text_input("Allowed Square Footage")
    changer_count = st.text_input("Price Changers")

    st.markdown("**Panels Required**")
    bonfire = st.checkbox("Bonfire Panel")
    trv = st.checkbox("Trucks & RVs Panel")
    ethanol = st.checkbox("Ethanol-Free Panel")
    nitro = st.checkbox("Nitro Panel")

    if st.button("Find Closest Matches"):
        try:
            sqft_val = float(square_footage)
            changers_val = int(changer_count)
        except ValueError:
            st.error("Please enter a valid number for square footage and price changers.")
            st.stop()

        def filter_and_score(row):
            panel_penalty = 0
            for panel, name in [(bonfire, "bonfire"), (trv, "trv"), (ethanol, "ethanol"), (nitro, "nitro")]:
                if panel and not row.get(name):
                    panel_penalty += 1
            if row["changer_count"] != changers_val:
                return float('inf')
            if row["square_footage"] > sqft_val:
                return float('inf')
            return panel_penalty

        df["score"] = df.apply(filter_and_score, axis=1)
        filtered = df[df["score"] < float("inf")].copy()
        filtered["leftover_sqft"] = (sqft_val - filtered["square_footage"]).round(2)
        top_matches = filtered.sort_values(by=["score", "leftover_sqft"], ascending=[True, True]).head(3).reset_index(drop=True)

        if top_matches.empty:
            st.warning("No matching drawings found.")
        else:
            st.subheader("Top 3 Matches")
            for i in range(len(top_matches)):
                row = top_matches.iloc[i]
                st.markdown("---")
                cols = st.columns([3, 1])

                with cols[0]:
                    st.markdown(f"**File Name:** {row['file_name']}")
                    st.markdown(f"**Leftover Square Footage:** {row['leftover_sqft']} sq ft")
                    panels = []
                    for p in ["bonfire", "trv", "ethanol", "nitro"]:
                        if row.get(p): panels.append(p.upper())
                    st.markdown(f"**Panels:** {'-'.join(panels) if panels else 'None'}")

                with cols[1]:
                    if row.get("preview_url"):
                        st.image(row["preview_url"], use_container_width=True)

                    if row.get("supabase_url"):
                        try:
                            response = requests.get(row["supabase_url"])
                            if response.status_code == 200:
                                st.download_button(
                                    label="Download PDF",
                                    data=response.content,
                                    file_name=row["file_name"],
                                    mime="application/pdf",
                                    key=row["file_name"]
                                )
                            else:
                                st.error(f"Could not fetch PDF (status {response.status_code})")
                        except Exception as e:
                            st.error(f"Download error: {e}")