"""
tab_pensions.py — Onglet 3 : Mapping pensions ORX et BKG vers valeurs normalisées.
"""

from __future__ import annotations

import streamlit as st

from config.constants import PENSIONS_NORM
from core.normalizer import build_reverse_maps
from ui.components import step_title


def render(
    orx_pensions_raw:   list[str],
    bkg_meal_plans_raw: list[str],
) -> dict[str, dict[str, list[str]]]:
    """
    Affiche les expanders de mapping pension.
    Retourne pension_config : {norm_label: {"orx": [...], "bkg": [...]}}.
    """
    step_title(3, "Mapping — Pensions / Meal Plans")
    st.caption(
        "Pour chaque valeur normalisée, associez les libellés ORX ET les libellés BKG. "
        "La comparaison s'effectuera uniquement entre pensions de même type normalisé."
    )
    st.markdown("")

    pension_config: dict[str, dict[str, list[str]]] = {}

    for norm in PENSIONS_NORM:
        with st.expander(f"🍽️  **{norm}**", expanded=False):
            col_orx, col_bkg = st.columns(2, gap="medium")

            with col_orx:
                st.markdown("**Sources ORX** *(colonne : Pension)*")
                orx_vals = st.multiselect(
                    "orx", options=orx_pensions_raw, key=f"p_orx__{norm}",
                    label_visibility="collapsed", placeholder="Libellés ORX...",
                )
            with col_bkg:
                st.markdown("**Sources BKG** *(colonne : Meal Plan)*")
                bkg_vals = st.multiselect(
                    "bkg", options=bkg_meal_plans_raw, key=f"p_bkg__{norm}",
                    label_visibility="collapsed", placeholder="Libellés BKG...",
                )

            pension_config[norm] = {"orx": orx_vals, "bkg": bkg_vals}

    # Avertissements libellés non mappés
    orx_p_rev, bkg_m_rev, _ = build_reverse_maps(pension_config, {})
    unmapped_orx = [v for v in orx_pensions_raw   if v not in orx_p_rev]
    unmapped_bkg = [v for v in bkg_meal_plans_raw if v not in bkg_m_rev]

    if unmapped_orx:
        st.warning(f"⚠️ Libellés ORX non mappés : {', '.join(unmapped_orx)}")
    if unmapped_bkg:
        st.warning(f"⚠️ Libellés BKG non mappés : {', '.join(unmapped_bkg)}")

    return pension_config
