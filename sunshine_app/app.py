import streamlit as st
import pandas as pd
import requests
from supabase_table_client import get_all_drawings

st.set_page_config(layout="wide")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("Sunshine Drawing Lookup")

    @st.cache_data
    def load_and_rank_drawings(sqft_val, changers_val, bonfire, trv, ethanol, nitro):
        drawings = get_all_drawings()
        df = pd.DataFrame(drawings)
        for field in ["square_footage", "changer_count"]:
            df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

        def compute_ranking(row):
            leftover_sqft = sqft_val - row["square_footage"]
            if leftover_sqft < 0:
                return None

            changer_diff = abs(row["changer_count"] - changers_val)
            panel_penalty = 0
            for panel, name in [(bonfire, "bonfire"), (trv, "trv"), (ethanol, "ethanol"), (nitro, "nitro")]:
                if panel and not row.get(name):
                    panel_penalty += 1

            score = leftover_sqft * 1.5 + changer_diff * 5 + panel_penalty * 2

            return pd.Series({
                "leftover_sqft": round(leftover_sqft, 2),
                "changer_diff": changer_diff,
                "panel_penalty": panel_penalty,
                "score": round(score, 2)
            })

        ranked = df.apply(compute_ranking, axis=1)
        df = df.join(ranked)
        df = df.dropna(subset=["score"])
        return df.sort_values(by="score").reset_index(drop=True)

    st.subheader("Search Criteria")
    square_footage = st.text_input("Allowed Square Footage")
    changer_count = st.text_input("Price Changers")

    st.markdown("**Panels Required**")
    bonfire = st.checkbox("Bonfire Panel")
    trv = st.checkbox("Trucks & RVs Panel")
    ethanol = st.checkbox("Ethanol-Free Panel")
    nitro = st.checkbox("Nitro Panel")

    if "page" not in st.session_state:
        st.session_state.page = 0
    if "sorted_df" not in st.session_state:
        st.session_state.sorted_df = pd.DataFrame()

    if st.button("Find Closest Matches"):
        try:
            sqft_val = float(square_footage)
            changers_val = int(changer_count)
        except ValueError:
            st.error("Please enter valid numbers.")
            st.stop()

        sorted_df = load_and_rank_drawings(sqft_val, changers_val, bonfire, trv, ethanol, nitro)
        st.session_state.sorted_df = sorted_df
        st.session_state.page = 0

    sorted_df = st.session_state.sorted_df
    page = st.session_state.page
    page_size = 5
    start = page * page_size
    end = start + page_size
    matches = sorted_df.iloc[start:end]

    if not matches.empty:
        st.subheader(f"Matches {start + 1}–{min(end, len(sorted_df))} of {len(sorted_df)}")
        for _, row in matches.iterrows():
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**File Name:** {row['file_name']}")
                st.markdown(f"**Leftover Square Footage:** {row['leftover_sqft']} sq ft")
                panels = [p.upper() for p in ["bonfire", "trv", "ethanol", "nitro"] if row.get(p)]
                st.markdown(f"**Panels:** {'-'.join(panels) if panels else 'None'}")
                st.markdown(f"**Changer Count:** {row['changer_count']}")
                st.markdown(f"**Dimensions:** {row['width']} x {row['height']}")

            with cols[1]:
                if row.get("preview_url"):
                    try:
                        st.image(row["preview_url"], width=250)
                    except Exception:
                        st.text("Image preview failed.")

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

            st.markdown("---")

        nav_cols = st.columns(2)
        if page > 0:
            if nav_cols[0].button("Previous Page"):
                st.session_state.page -= 1
                st.rerun()
        if end < len(sorted_df):
            if nav_cols[1].button("Next Page"):
                st.session_state.page += 1
                st.rerun()