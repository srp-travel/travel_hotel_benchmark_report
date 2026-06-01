#!/usr/bin/env python3
"""
Benchmark Tarifaire ORX vs Booking.com
Point d'entrée minimal — toute la logique est dans core/ et ui/
Usage : streamlit run app.py
"""

import streamlit as st

from ui.styles import inject_css
from ui.tabs import render_all_tabs


st.set_page_config(
    page_title="Benchmark Tarifaire",
    page_icon="🏨",
    layout="wide",
)

inject_css()

st.markdown("# 🏨 Benchmark Tarifaire")
st.caption("Analyse de compétitivité tarifaire — ORX (Orchestra) vs Booking.com")
st.markdown("---")

render_all_tabs()