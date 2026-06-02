"""
tab_params.py — Onglet 1 : Configuration des seuils de compétitivité et décote Genius.

Les widgets ont des clés session_state explicites pour permettre la restauration
automatique depuis un fichier de config JSON (config_persistence.py).

Clés exposées :
  ref_policy_input    → selectbox politique d'annulation
  seuil_proche_input  → number_input seuil non compétitif / proche  (entier %)
  seuil_comp_input    → number_input seuil proche / compétitif       (entier %)
  seuil_tres_input    → number_input seuil compétitif / très comp.   (entier %)
  genius_input        → number_input décote Genius                   (entier %)
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config.constants import (
    ANNULATIONS_NORM,
    DEFAULT_GENIUS_DECOTE,
    DEFAULT_SEUIL_PROCHE,
    DEFAULT_SEUIL_COMPETITIF,
    DEFAULT_SEUIL_TRES_COMPETITIF,
)
from ui.components import step_title


def render() -> dict[str, float]:
    """
    Affiche le formulaire des paramètres.
    Retourne le dict `params` utilisé par run_matching() et get_competitiveness().
    """
    step_title(1, "Paramètres de benchmark")

    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown("**Politique d'annulation de référence ORX**")
        ref_policy: str = st.selectbox(
            "ref_policy",
            options=ANNULATIONS_NORM,
            key="ref_policy_input",            # ← clé session_state pour restauration
            label_visibility="collapsed",
        )
        st.info(f"Référence ORX : **{ref_policy}**")

        # ── Décote Genius ──────────────────────────────────────
        st.markdown("---")
        st.markdown("**Décote Genius BKG** *(% appliqué à tous les prix Booking)*")
        st.caption(
            "Simule le prix affiché aux membres Genius. "
            "Un prix BKG de 100 € avec une décote de 10 % sera comparé à 90 €. "
            "Mettre 0 pour désactiver."
        )
        genius_decote_pct: int = st.number_input(
            "genius_decote",
            value=DEFAULT_GENIUS_DECOTE,
            min_value=0,
            max_value=50,
            step=1,
            format="%d",
            key="genius_input",                # ← clé session_state pour restauration
            label_visibility="collapsed",
        )
        genius_decote = genius_decote_pct / 100

        if genius_decote > 0:
            st.info(
                f"💡 Prix BKG comparés après décote de **{genius_decote_pct}%** "
                f"— colonne **Prix BKG Genius** visible dans le rapport."
            )

    with col_b:
        st.markdown("**Seuils de compétitivité** *(valeurs négatives en %)*")
        st.caption("Ecart = (Prix ORX - Prix BKG comparé) / Prix BKG comparé")

        seuil_proche: int = st.number_input(
            "Seuil Non compétitif / Proche",
            value=DEFAULT_SEUIL_PROCHE,
            min_value=-99, max_value=0, step=1, format="%d",
            key="seuil_proche_input",          # ← clé session_state pour restauration
        )
        seuil_competitif: int = st.number_input(
            "Seuil Proche / Compétitif",
            value=DEFAULT_SEUIL_COMPETITIF,
            min_value=-99, max_value=0, step=1, format="%d",
            key="seuil_comp_input",            # ← clé session_state pour restauration
        )
        seuil_tres_competitif: int = st.number_input(
            "Seuil Compétitif / Très compétitif",
            value=DEFAULT_SEUIL_TRES_COMPETITIF,
            min_value=-99, max_value=0, step=1, format="%d",
            key="seuil_tres_input",            # ← clé session_state pour restauration
        )

    st.markdown("---")
    st.dataframe(
        pd.DataFrame([
            {"Indicateur": "❌ Non compétitif",  "Condition": f"Ecart > {seuil_proche}%"},
            {"Indicateur": "⚠️ Proche",          "Condition": f"{seuil_competitif}% < Ecart ≤ {seuil_proche}%"},
            {"Indicateur": "✅ Compétitif",       "Condition": f"{seuil_tres_competitif}% < Ecart ≤ {seuil_competitif}%"},
            {"Indicateur": "✅ Très compétitif",  "Condition": f"Ecart ≤ {seuil_tres_competitif}%"},
        ]),
        hide_index=True,
        use_container_width=True,
    )

    # Stockage de la politique de référence pour tab_report
    st.session_state["ref_policy"] = ref_policy

    return {
        "seuil_non_competitif":  seuil_proche         / 100,
        "seuil_competitif":      seuil_competitif      / 100,
        "seuil_tres_competitif": seuil_tres_competitif / 100,
        "genius_decote":         genius_decote,
    }