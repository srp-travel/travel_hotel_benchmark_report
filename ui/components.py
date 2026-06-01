"""
components.py — Micro-composants Streamlit réutilisables dans tous les onglets.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config.constants import ROW_COLORS, SEUIL_LABELS


def step_title(n: int, label: str) -> None:
    """Affiche un titre d'étape numéroté avec badge circulaire."""
    st.markdown(
        f'<div class="step-title">'
        f'<span class="step-badge">{n}</span>{label}'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")


def kpi(label: str, value: str, cls: str = "") -> None:
    """Affiche une ligne KPI label / valeur avec colorisation optionnelle."""
    st.markdown(
        f'<div class="kpi-row">'
        f'<span class="kpi-label">{label}</span>'
        f'<span class="kpi-value {cls}">{value}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_seuil_stats(df_scored: pd.DataFrame, n_comparable: int) -> None:
    """Affiche la répartition des niveaux de compétitivité sous forme de lignes colorées."""
    comp_counts = df_scored["_competitivite"].value_counts()
    for label, _cls, bg in SEUIL_LABELS:
        count = int(comp_counts.get(label, 0))
        pct   = count / n_comparable if n_comparable else 0.0
        st.markdown(
            f'<div class="seuil-row" style="background:{bg};">'
            f'<span class="seuil-label">{label}</span>'
            f'<span>'
            f'<span class="seuil-count">{count:,}</span>'
            f'<span class="seuil-pct">({pct:.1%})</span>'
            f'</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_legend() -> None:
    """Affiche la légende des couleurs de compétitivité."""
    items = [
        ("#C6EFCE", "Très compétitif"),
        ("#E2EFDA", "Compétitif"),
        ("#FFEB9C", "Proche"),
        ("#FFC7CE", "Non compétitif"),
        ("#F2F2F2", "N/A"),
    ]
    st.markdown(
        '<div class="legend-wrap">'
        + "".join(
            f'<div class="legend-item">'
            f'<div class="legend-dot" style="background:{c};"></div>{lbl}'
            f'</div>'
            for c, lbl in items
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def render_coverage_block(df: pd.DataFrame) -> None:
    """Affiche le bloc de couverture des dates de départ avec barre de progression."""
    from core.scoring import compute_date_coverage

    tw   = compute_date_coverage(df)
    rate = float(tw["rate"])  # type: ignore[arg-type]
    bar_color = "#375623" if rate >= 0.8 else "#9C6500" if rate >= 0.4 else "#C00000"
    bar_w     = int(rate * 100)

    with st.container(border=True):
        st.markdown(
            '<div class="kpi-section-title">Couverture des dates de départ</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Pour chaque combinaison (Date de départ x Nb nuits), "
            "vérifie si une correspondance BKG de même pension existe."
        )

        tw1, tw2, tw3 = st.columns(3)
        tw1.metric("Combinaisons totales",    str(tw["total"]))
        tw2.metric("Avec correspondance BKG", str(tw["covered"]))
        missing_val = int(tw["missing"])  # type: ignore[arg-type]
        tw3.metric(
            "Sans correspondance", str(missing_val),
            delta=f"-{missing_val}" if missing_val > 0 else None,
            delta_color="inverse",
        )
        st.markdown(
            f'<div style="margin:8px 0 4px 0;font-size:14px;font-weight:600;color:{bar_color};">'
            f'Taux de couverture : {rate:.1%}</div>'
            f'<div class="tw-bar-wrap">'
            f'<div class="tw-bar-fill" style="width:{bar_w}%;background:{bar_color};"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        with st.expander("Détail par date de départ", expanded=False):
            detail = tw["detail"].copy()  # type: ignore[union-attr]
            detail["Statut"] = detail["_has_bkg"].map(  # type: ignore[index]
                {True: "✅ Couverte", False: "❌ Manquante"}
            )
            st.dataframe(
                detail[["Date de départ", "Nb nuits", "Statut"]],  # type: ignore[index]
                hide_index=True,
                use_container_width=True,
            )


def render_footer() -> None:
    st.markdown(
        '<div class="app-footer">'
        "🏨 Benchmark Tarifaire ORX vs Booking.com &nbsp;·&nbsp; "
        "<strong>Salah CHERKAOUI</strong> &nbsp;·&nbsp; Equipe projet Voyage &amp; Loisirs"
        "</div>",
        unsafe_allow_html=True,
    )
