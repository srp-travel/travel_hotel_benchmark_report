"""
tabs/__init__.py — Orchestration des onglets de l'application.
C'est ici qu'on importe et appelle chaque onglet dans l'ordre.
"""

from __future__ import annotations

import streamlit as st

from core.data_loader import load_data, safe_unique
from ui.components import render_footer
from ui.tabs.tab_guide    import render as render_guide
from ui.tabs.tab_params   import render as render_params
from ui.tabs.tab_rooms    import render as render_rooms
from ui.tabs.tab_pensions import render as render_pensions
from ui.tabs.tab_cancel   import render as render_cancel
from ui.tabs.tab_report   import render as render_report


def render_all_tabs() -> None:
    """
    Point d'entrée principal de l'UI :
    1. Upload du fichier
    2. Chargement des données
    3. Rendu des 6 onglets
    """
    st.markdown("### 📂 Étape 0 — Chargement du fichier")
    uploaded = st.file_uploader(
        "Fichier .xlsx — feuilles attendues : 1. INPUT ORX EXPORT  |  2. OUTPUT BKG SCRAP",
        type=["xlsx"],
    )

    if uploaded is None:
        st.info("👆 Chargez votre fichier Excel pour démarrer la configuration.")
        render_footer()
        return

    file_bytes = uploaded.read()
    try:
        df_orx, df_bkg = load_data(file_bytes)
    except Exception as e:
        st.error(f"❌ Erreur de lecture : {e}")
        render_footer()
        return

    # -- Résumé du chargement
    bkg_hotel_col   = str(df_bkg.columns[0])
    orx_categories  = safe_unique(df_orx, "Catégorie")
    orx_pensions    = safe_unique(df_orx, "Pension")
    bkg_room_types  = safe_unique(df_bkg, "Room Type")
    bkg_meal_plans  = safe_unique(df_bkg, "Meal Plan")
    bkg_cancel_raw  = safe_unique(df_bkg, "Cancellation Policy")

    c1, c2 = st.columns(2)
    c1.success(
        f"✅ ORX — {len(df_orx):,} lignes · {len(orx_categories)} catégorie(s) · "
        f"{len(orx_pensions)} libellé(s) pension"
    )
    c2.success(
        f"✅ BKG — {len(df_bkg):,} lignes · {len(bkg_room_types)} type(s) de chambre · "
        f"{len(bkg_cancel_raw)} politique(s) d'annulation"
    )
    st.caption(f"🏨 Colonne hôtel (BKG col. 1) : **{bkg_hotel_col}**")
    st.markdown("---")

    # -- Onglets
    tabs = st.tabs([
        "📖  Guide",
        "⚙️  1 · Paramètres",
        "🛏️  2 · Chambres",
        "🍽️  3 · Pensions",
        "📋  4 · Annulation",
        "📊  5 · Rapport",
    ])

    with tabs[0]: render_guide()
    with tabs[1]: params        = render_params()
    with tabs[2]: room_mapping  = render_rooms(orx_categories, bkg_room_types)
    with tabs[3]: pension_config = render_pensions(orx_pensions, bkg_meal_plans)
    with tabs[4]: cancel_config  = render_cancel(bkg_cancel_raw, pension_config)
    with tabs[5]: render_report(
        df_orx, df_bkg,
        room_mapping, pension_config, cancel_config,
        params, file_bytes,
    )

    render_footer()