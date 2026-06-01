"""
tab_params.py — Onglet 1 : Configuration des seuils de compétitivité et décote Genius.
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

    Clés retournées :
      - seuil_non_competitif   : float (ex. -0.10)
      - seuil_competitif       : float (ex. -0.15)
      - seuil_tres_competitif  : float (ex. -0.20)
      - genius_decote          : float (ex. 0.10 pour 10%)
    """
    step_title(1, "Paramètres de benchmark")

    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown("**Politique d'annulation de référence ORX**")
        ref_policy = st.selectbox(
            "ref_policy",
            options=ANNULATIONS_NORM,
            index=ANNULATIONS_NORM.index("RF - Remboursable"),
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
        genius_decote_pct = st.number_input(
            "genius_decote",
            value=DEFAULT_GENIUS_DECOTE,
            min_value=0,
            max_value=50,
            step=1,
            format="%d",
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

        seuil_proche = st.number_input(
            "Seuil Non compétitif / Proche",
            value=DEFAULT_SEUIL_PROCHE,
            min_value=-99, max_value=0, step=1, format="%d",
        ) / 100

        seuil_competitif = st.number_input(
            "Seuil Proche / Compétitif",
            value=DEFAULT_SEUIL_COMPETITIF,
            min_value=-99, max_value=0, step=1, format="%d",
        ) / 100

        seuil_tres_competitif = st.number_input(
            "Seuil Compétitif / Très compétitif",
            value=DEFAULT_SEUIL_TRES_COMPETITIF,
            min_value=-99, max_value=0, step=1, format="%d",
        ) / 100

    st.markdown("---")
    st.dataframe(
        pd.DataFrame([
            {"Indicateur": "❌ Non compétitif",  "Condition": f"Ecart > {int(seuil_proche*100)}%"},
            {"Indicateur": "⚠️ Proche",          "Condition": f"{int(seuil_competitif*100)}% < Ecart ≤ {int(seuil_proche*100)}%"},
            {"Indicateur": "✅ Compétitif",       "Condition": f"{int(seuil_tres_competitif*100)}% < Ecart ≤ {int(seuil_competitif*100)}%"},
            {"Indicateur": "✅ Très compétitif",  "Condition": f"Ecart ≤ {int(seuil_tres_competitif*100)}%"},
        ]),
        hide_index=True,
        use_container_width=True,
    )

    # Stockage de la politique de référence pour tab_report
    st.session_state["ref_policy"] = ref_policy

    return {
        "seuil_non_competitif":  float(seuil_proche),
        "seuil_competitif":      float(seuil_competitif),
        "seuil_tres_competitif": float(seuil_tres_competitif),
        "genius_decote":         float(genius_decote),
    }