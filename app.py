import streamlit as st
import os
from dotenv import load_dotenv
from graph import run_research
# Set the page config
st.set_page_config(page_title="Ask Birdy", layout="wide")

# Title
st.title("🔍 Ask Birdy")
st.markdown("Get a well-researched summary on any topic.")

# Input
topic = st.text_input("Enter a topic to research", placeholder="e.g., renewable energy breakthroughs 2025")

if st.button("Run Research", type="primary"):
    if topic:
        with st.spinner("🔎 Researching and generating report..."):
            try:
                result = run_research(topic)
                st.markdown("## 📄 Your Research Summary")
                st.markdown(result)
                st.balloons()
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic.")