import streamlit as st
import pandas as pd
from supabase_table_client import get_all_drawings

st.set_page_config(layout="wide")
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

# UI layout with three columns for consistent margins
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.subheader("Search Criteria")
    square_footage = st.number_input("Allowed Square Footage", min_value=0.0, step=0.25)
    changer_count = st.number_input("Price Changer Count", min_value=0, step=1)

    st.markdown("**Panels Required**")
    bonfire = st.checkbox("Bonfire Panel")
    trv = st.checkbox("Trucks & RVs Panel")
    ethanol = st.checkbox("Ethanol-Free Panel")
    nitro = st.checkbox("Nitro Panel")

    if st.button("Find Closest Matches"):
        def score(row):
            score = 0

            if row["changer_count"] == changer_count:
                score += 5
            else:
                score -= abs(row["changer_count"] - changer_count)

            if row["square_footage"] <= square_footage:
                score += 5
            else:
                score -= 10

            for panel, name in [(bonfire, "bonfire"), (trv, "trv"), (ethanol, "ethanol"), (nitro, "nitro")]:
                if panel:
                    score += 3 if row.get(name) else -5
            return score

        df["score"] = df.apply(score, axis=1)
        top_matches = df.sort_values("score", ascending=False).head(3)

        st.subheader("Top 3 Matches")
        for _, row in top_matches.iterrows():
            st.markdown("---")
            cols = st.columns([3, 1])

            with cols[0]:
                st.markdown(f"**File Name:** {row['file_name']}")
                st.markdown(f"**Score:** {row['score']}")
                st.markdown(f"**Square Footage:** {row['square_footage']} sq ft")
                st.markdown(f"**Digit Size:** {row['digit_size']}")
                st.markdown(f"**Changer Count:** {row['changer_count']}")
                st.markdown(f"**Dimensions:** {row['width']} x {row['height']}")
                panels = []
                for p in ["bonfire", "trv", "ethanol", "nitro"]:
                    if row.get(p): panels.append(p.upper())
                st.markdown(f"**Panels:** {'-'.join(panels) if panels else 'None'}")

            with cols[1]:
                if row.get("preview_url"):
                    st.image(row["preview_url"], use_container_width=True)