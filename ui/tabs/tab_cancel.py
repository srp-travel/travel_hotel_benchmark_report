"""
tab_cancel.py — Onglet 4 : Mapping politiques d'annulation BKG vers valeurs normalisées.

Contient également la sélection de la politique d'annulation de référence ORX,
déplacée ici depuis tab_params pour regrouper tout ce qui concerne l'annulation.

Clés session_state exposées :
  ref_policy_input  → selectbox politique d'annulation de référence ORX
  c_bkg__{norm}     → multiselect mapping BKG par politique normalisée
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
    Affiche la politique de référence ORX et les expanders de mapping annulation.
    Retourne cancel_config : {norm_label: {"bkg": [...]}}.
    """
    step_title(4, "Mapping — Politiques d'annulation")
    st.markdown("")

    # ── Politique d'annulation de référence ORX ───────────────
    st.markdown("**Politique d'annulation de référence ORX**")
    st.caption(
        "Sélectionnez la politique normalisée qui représente votre offre ORX. "
        "Elle est utilisée dans le rapport pour identifier les comparaisons à politique équivalente."
    )
    ref_policy: str = st.selectbox(
        "ref_policy",
        options=ANNULATIONS_NORM,
        key="ref_policy_input",                # ← clé session_state pour restauration
        label_visibility="collapsed",
    )
    st.info(f"Référence ORX sélectionnée : **{ref_policy}**")

    st.markdown("---")

    # ── Mapping BKG → valeurs normalisées ─────────────────────
    st.markdown("**Correspondances BKG**")
    st.caption("Associez chaque libellé brut Booking.com à une politique normalisée.")
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

    # Stockage session_state pour tab_report
    st.session_state["ref_policy"] = ref_policy

    return cancel_config