"""
styles.py — Injection du CSS global de l'application.
Modifier uniquement ce fichier pour ajuster le thème visuel.
"""

import streamlit as st


_CSS = """
<style>
    html, body, [class*="css"] { font-size: 15px; }
    .main .block-container { padding-top: 1.5rem; max-width: 1440px; }

    /* Titres d'étape */
    .step-title {
        display: flex; align-items: center; gap: 10px;
        font-size: 18px; font-weight: 700; color: #1F3864; margin: 0 0 8px 0;
    }
    .step-badge {
        display: inline-flex; align-items: center; justify-content: center;
        min-width: 28px; height: 28px; background: #1F3864; color: white;
        border-radius: 50%; font-size: 14px; font-weight: 700;
    }

    /* En-tête rapport */
    .bench-title    { font-size: 24px; font-weight: 700; color: #1F3864; margin-bottom: 3px; }
    .bench-subtitle { font-size: 15px; color: #555; margin-bottom: 16px; }

    /* KPI */
    .kpi-section-title {
        font-size: 13px; font-weight: 700; text-transform: uppercase;
        letter-spacing: .07em; color: #1F3864;
        border-bottom: 2px solid #1F3864; padding-bottom: 5px; margin: 14px 0 10px 0;
    }
    .kpi-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 6px 0; border-bottom: 1px solid #F0F0F0;
    }
    .kpi-label  { font-size: 14px; color: #444; }
    .kpi-value  { font-size: 15px; font-weight: 600; color: #1F3864; }
    .kpi-value.danger  { color: #C00000; }
    .kpi-value.warning { color: #9C6500; }
    .kpi-value.success { color: #375623; }

    /* Seuils */
    .seuil-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 10px; border-radius: 6px; margin-bottom: 6px;
    }
    .seuil-label { font-size: 14px; font-weight: 500; }
    .seuil-count { font-size: 15px; font-weight: 700; }
    .seuil-pct   { font-size: 13px; color: #555; margin-left: 6px; }

    /* Barre de progression couverture */
    .tw-bar-wrap {
        background: #E8E8E8; border-radius: 20px; height: 16px;
        overflow: hidden; margin: 8px 0 2px 0;
    }
    .tw-bar-fill { height: 100%; border-radius: 20px; transition: width .4s; }

    /* Légende */
    .legend-wrap  { display: flex; gap: 20px; flex-wrap: wrap; margin: 8px 0 14px 0; align-items: center; }
    .legend-item  { display: flex; align-items: center; gap: 7px; font-size: 14px; }
    .legend-dot   { width: 16px; height: 16px; border-radius: 4px; flex-shrink: 0; border: 1px solid #ccc; }

    /* Pagination */
    .pagination-bar {
        display: flex; align-items: center; justify-content: center;
        gap: 14px; padding: 8px 0; font-size: 15px; color: #1F3864;
    }

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { padding: 9px 20px; border-radius: 6px 6px 0 0; font-size: 14px; }

    /* Bouton téléchargement */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1F3864 0%, #2E5FA3 100%) !important;
        color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
        font-size: 15px !important; font-weight: 600 !important; letter-spacing: 0.04em !important;
        padding: 14px 28px !important; box-shadow: 0 3px 10px rgba(31,56,100,.35) !important;
        transition: all 0.2s ease !important; width: 100% !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #162A4E 0%, #1F4A8A 100%) !important;
        box-shadow: 0 6px 18px rgba(31,56,100,.45) !important; transform: translateY(-2px) !important;
    }
    .stDownloadButton > button:active {
        transform: translateY(0px) !important; box-shadow: 0 2px 6px rgba(31,56,100,.3) !important;
    }

    /* Footer */
    .app-footer {
        text-align: center; padding: 24px 0 12px 0; font-size: 13px; color: #888;
        border-top: 1px solid #E8E8E8; margin-top: 40px;
    }
    .app-footer strong { color: #1F3864; font-weight: 600; }
</style>
"""


def inject_css() -> None:
    """Injecte le CSS global dans la page Streamlit."""
    st.markdown(_CSS, unsafe_allow_html=True)
