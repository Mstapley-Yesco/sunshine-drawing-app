import streamlit as st
import requests
from supabase_table_client import get_all_drawings

st.set_page_config(layout="wide")
st.title("📂 View Uploaded Drawings")

drawings = get_all_drawings()

if not drawings:
    st.info("No drawings found.")
else:
    for drawing in sorted(drawings, key=lambda x: (int(x.get("digit_size", "0IN").replace("IN", "") or 0), x.get("changer_count", 0))):
        st.markdown("---")
        cols = st.columns([3, 1])

        with cols[0]:
            st.markdown(f"**File Name:** {drawing.get('file_name', 'N/A')}")
            st.markdown(f"**Square Footage:** {drawing.get('square_footage', 'N/A')} sq ft")
            st.markdown(f"**Digit Size:** {drawing.get('digit_size', 'N/A')}")
            st.markdown(f"**Changer Count:** {drawing.get('changer_count', 'N/A')}")
            st.markdown(f"**Dimensions:** {drawing.get('width', 'N/A')} x {drawing.get('height', 'N/A')}")
            panels = []
            if drawing.get("bonfire"): panels.append("BON")
            if drawing.get("trv"): panels.append("TRV")
            if drawing.get("ethanol"): panels.append("ETH")
            if drawing.get("nitro"): panels.append("NITRO")
            st.markdown(f"**Panels:** {'-'.join(panels) if panels else 'None'}")

        with cols[1]:
            if drawing.get("preview_url"):
                st.image(drawing["preview_url"], use_container_width=True)
            else:
                st.markdown("_No preview available_")

            if drawing.get("supabase_url"):
                try:
                    response = requests.get(drawing["supabase_url"])
                    if response.status_code == 200:
                        st.download_button(
                            label="Download PDF",
                            data=response.content,
                            file_name=drawing["file_name"],
                            mime="application/pdf",
                            key=f"download_{drawing['file_name']}"
                        )
                    else:
                        st.error(f"Failed to fetch PDF (status {response.status_code})")
                except Exception as e:
                    st.error(f"Download error: {e}")
