"""
tabs/__init__.py — Orchestration des onglets de l'application.

Ordre de rendu :
  1. Guide             — toujours visible, avant le file uploader.
  2. File uploader     — chargement du fichier Excel.
  3. Couverture brute  — Travel Window avant mapping.
  4. Config bar        — sauvegarde / restauration du mapping JSON.
  5. Onglets           — configuration et rapport (après chargement).
"""

from __future__ import annotations

__all__ = ["render_all_tabs"]

import streamlit as st

from core.data_loader import load_data, safe_unique
from ui.components import render_footer, render_raw_coverage_block
from ui.config_bar import render_config_bar
from ui.tabs.tab_cancel import render as render_cancel
from ui.tabs.tab_guide import render as render_guide
from ui.tabs.tab_params import render as render_params
from ui.tabs.tab_pensions import render as render_pensions
from ui.tabs.tab_report import render as render_report
from ui.tabs.tab_rooms import render as render_rooms


def render_all_tabs() -> None:
    """Point d'entrée principal de l'UI."""

    # ── 1. GUIDE — toujours visible ───────────────────────────
    with st.expander("📖 Guide d'utilisation", expanded=False):
        render_guide()

    st.markdown("---")

    # ── 2. CHARGEMENT ─────────────────────────────────────────
    st.markdown("### 📂 Chargement du fichier")
    uploaded = st.file_uploader(
        "Fichier .xlsx — feuilles attendues : 1. INPUT ORX EXPORT  |  2. OUTPUT BKG SCRAP",
        type=["xlsx"],
    )

    if uploaded is None:
        st.info("👆 Chargez votre fichier Excel pour accéder aux onglets de configuration et au rapport.")
        render_footer()
        return

    file_bytes = uploaded.read()

    try:
        df_orx, df_bkg = load_data(file_bytes)
    except Exception as e:
        st.error(f"❌ Erreur de lecture : {e}")
        render_footer()
        return

    # ── Résumé du chargement ───────────────────────────────────
    bkg_hotel_col  = str(df_bkg.columns[0])
    orx_categories = safe_unique(df_orx, "Catégorie")
    orx_pensions   = safe_unique(df_orx, "Pension")
    bkg_room_types = safe_unique(df_bkg, "Room Type")
    bkg_meal_plans = safe_unique(df_bkg, "Meal Plan")
    bkg_cancel_raw = safe_unique(df_bkg, "Cancellation Policy")

    c1, c2 = st.columns(2)
    c1.success(
        f"✅ ORX — {len(df_orx):,} lignes · "
        f"{len(orx_categories)} catégorie(s) · "
        f"{len(orx_pensions)} libellé(s) pension"
    )
    c2.success(
        f"✅ BKG — {len(df_bkg):,} lignes · "
        f"{len(bkg_room_types)} type(s) de chambre · "
        f"{len(bkg_cancel_raw)} politique(s) d'annulation"
    )
    st.caption(f"🏨 Colonne hôtel (BKG col. 1) : **{bkg_hotel_col}**")

    # ── 3. COUVERTURE BRUTE ────────────────────────────────────
    st.markdown("")
    render_raw_coverage_block(df_orx, df_bkg)

    st.markdown("---")

    # ── 4. BARRE DE CONFIG ────────────────────────────────────
    render_config_bar()

    st.markdown("---")

    # ── 5. ONGLETS ────────────────────────────────────────────
    tab_params, tab_rooms, tab_pensions, tab_cancel, tab_report = st.tabs([
        "⚙️  1 · Paramètres",
        "🛏️  2 · Chambres",
        "🍽️  3 · Pensions",
        "📋  4 · Annulation",
        "📊  5 · Rapport",
    ])

    with tab_params:
        params = render_params()

    with tab_rooms:
        room_mapping = render_rooms(orx_categories, bkg_room_types)

    with tab_pensions:
        pension_config = render_pensions(orx_pensions, bkg_meal_plans)

    with tab_cancel:
        cancel_config = render_cancel(bkg_cancel_raw, pension_config)

    with tab_report:
        render_report(
            df_orx=df_orx,
            df_bkg=df_bkg,
            room_mapping=room_mapping,
            pension_config=pension_config,
            cancel_config=cancel_config,
            params=params,
            file_bytes=file_bytes,
        )

    render_footer()