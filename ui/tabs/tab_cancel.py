"""
tab_cancel.py — Onglet 4 : Mapping politiques d'annulation BKG vers valeurs normalisées.
"""

from __future__ import annotations

import streamlit as st

from config.constants import ANNULATIONS_NORM
from core.normalizer import build_reverse_maps
from ui.components import step_title


def render(
    bkg_cancel_raw: list[str],
    pension_config: dict[str, dict[str, list[str]]],
) -> dict[str, dict[str, list[str]]]:
    """
    Affiche les expanders de mapping annulation.
    Retourne cancel_config : {norm_label: {"bkg": [...]}}.
    """
    step_title(4, "Mapping — Politiques d'annulation")
    st.markdown("")

    cancel_config: dict[str, dict[str, list[str]]] = {}

    for norm in ANNULATIONS_NORM:
        with st.expander(f"📋  **{norm}**", expanded=False):
            st.markdown("**Sources BKG** *(colonne : Cancellation Policy)*")
            bkg_cancel_vals = st.multiselect(
                "bkg", options=bkg_cancel_raw, key=f"c_bkg__{norm}",
                label_visibility="collapsed", placeholder="Libellés BKG...",
            )
            cancel_config[norm] = {"bkg": bkg_cancel_vals}

    _, _, bkg_c_rev = build_reverse_maps(pension_config, cancel_config)
    unmapped = [v for v in bkg_cancel_raw if v not in bkg_c_rev]
    if unmapped:
        st.warning(f"⚠️ Politiques BKG non mappées : {', '.join(unmapped)}")

    return cancel_config
