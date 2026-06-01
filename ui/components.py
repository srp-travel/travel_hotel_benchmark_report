"""
components.py — Micro-composants Streamlit réutilisables dans tous les onglets.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from config.constants import ROW_COLORS, SEUIL_LABELS

__all__ = [
    "kpi",
    "render_coverage_block",
    "render_footer",
    "render_legend",
    "render_raw_coverage_block",
    "render_seuil_stats",
    "step_title",
]


# ── Titres & labels ────────────────────────────────────────────────────────────

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


# ── Helpers internes ───────────────────────────────────────────────────────────

def _coverage_bar(rate: float, bar_color: str, label: str) -> None:
    """Barre de progression réutilisable pour les blocs de couverture."""
    bar_w = int(rate * 100)
    st.markdown(
        f'<div style="margin:8px 0 4px 0;font-size:14px;font-weight:600;color:{bar_color};">'
        f'{label} : {rate:.1%}</div>'
        f'<div class="tw-bar-wrap">'
        f'<div class="tw-bar-fill" style="width:{bar_w}%;background:{bar_color};"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _badge(text: str, bg: str, color: str) -> None:
    st.markdown(
        f'<span style="font-size:12px;background:{bg};color:{color};'
        f'padding:3px 8px;border-radius:12px;font-weight:600;">{text}</span>',
        unsafe_allow_html=True,
    )


# ── Blocs de couverture ────────────────────────────────────────────────────────

def render_raw_coverage_block(df_orx: pd.DataFrame, df_bkg: pd.DataFrame) -> None:
    """
    Bloc de couverture BRUTE Travel Window.
    Affiché dès le chargement du fichier, avant tout mapping.
    Compare les dates de départ ORX aux Check-in BKG sans aucun filtrage.
    """
    from core.scoring import compute_raw_date_coverage

    tw: dict[str, Any] = compute_raw_date_coverage(df_orx, df_bkg)
    rate      = float(tw["rate"])
    bar_color = "#375623" if rate >= 0.8 else "#9C6500" if rate >= 0.4 else "#C00000"

    with st.container(border=True):
        col_title, col_badge = st.columns([6, 1])
        with col_title:
            st.markdown(
                '<div class="kpi-section-title">🗓️ Couverture Travel Window — Brute</div>',
                unsafe_allow_html=True,
            )
        with col_badge:
            _badge("Avant mapping", "#E8EFF8", "#1F3864")

        st.caption(
            "Comparaison brute des dates de départ ORX vs Check-in BKG, "
            "tous types de chambre et pensions confondus. "
            "Permet de détecter les trous de scraping avant toute configuration."
        )

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Dates ORX uniques",     str(tw["orx_total"]))
        m2.metric("Dates BKG disponibles", str(tw["bkg_total"]))
        m3.metric("Dates couvertes",        str(tw["covered"]))

        missing_val = int(tw["missing"])
        m4.metric(
            "Dates manquantes", str(missing_val),
            delta=f"-{missing_val}" if missing_val > 0 else None,
            delta_color="inverse",
        )
        extra_val = int(tw["extra_bkg"])
        m5.metric(
            "Dates BKG hors ORX", str(extra_val),
            help="Dates scrapées sur BKG sans offre ORX correspondante.",
        )

        _coverage_bar(rate, bar_color, "Taux de couverture brute")

        missing_dates: list[str] = tw["missing_dates"]
        if missing_dates:
            st.warning(
                f"⚠️ **{len(missing_dates)} date(s) ORX absente(s) du scraping BKG** — "
                f"ces offres seront N/A quel que soit le mapping : "
                f"{', '.join(missing_dates)}"
            )
        else:
            st.success("✅ Toutes les dates de départ ORX sont présentes dans le scraping BKG.")

        with st.expander("Détail date par date", expanded=False):
            detail: pd.DataFrame = tw["detail"]
            st.dataframe(
                detail.style.apply(
                    lambda row: [
                        "background-color: #C6EFCE" if "Présente" in str(row["Statut"])
                        else "background-color: #FFC7CE"
                    ] * len(row),
                    axis=1,
                ),
                hide_index=True,
                use_container_width=True,
            )


def render_coverage_block(df: pd.DataFrame) -> None:
    """
    Bloc de couverture ENRICHIE (post-génération).
    Par combinaison (Date de départ x Nb nuits), vérifie si une correspondance
    BKG avec mapping complet (chambre + pension) a été trouvée.
    """
    from core.scoring import compute_date_coverage

    tw: dict[str, Any] = compute_date_coverage(df)
    rate      = float(tw["rate"])
    bar_color = "#375623" if rate >= 0.8 else "#9C6500" if rate >= 0.4 else "#C00000"

    with st.container(border=True):
        col_title, col_badge = st.columns([6, 1])
        with col_title:
            st.markdown(
                '<div class="kpi-section-title">🗓️ Couverture Travel Window — Enrichie</div>',
                unsafe_allow_html=True,
            )
        with col_badge:
            _badge("Après mapping", "#E8F5E9", "#375623")

        st.caption(
            "Par combinaison (Date de départ x Nb nuits), vérifie si une correspondance "
            "BKG de même chambre et pension existe après application du mapping complet."
        )

        tw1, tw2, tw3 = st.columns(3)
        tw1.metric("Combinaisons totales",    str(tw["total"]))
        tw2.metric("Avec correspondance BKG", str(tw["covered"]))
        missing_val = int(tw["missing"])
        tw3.metric(
            "Sans correspondance", str(missing_val),
            delta=f"-{missing_val}" if missing_val > 0 else None,
            delta_color="inverse",
        )

        _coverage_bar(rate, bar_color, "Taux de couverture enrichie")

        with st.expander("Détail par date de départ", expanded=False):
            detail_df = tw["detail"].copy()
            detail_df["Statut"] = detail_df["_has_bkg"].map(
                {True: "✅ Couverte", False: "❌ Manquante"}
            )
            st.dataframe(
                detail_df[["Date de départ", "Nb nuits", "Statut"]],
                hide_index=True,
                use_container_width=True,
            )


# ── Footer ─────────────────────────────────────────────────────────────────────

def render_footer() -> None:
    st.markdown(
        '<div class="app-footer">'
        "🏨 Benchmark Tarifaire ORX vs Booking.com &nbsp;·&nbsp; "
        "<strong>Salah CHERKAOUI</strong> &nbsp;·&nbsp; Equipe projet Voyage &amp; Loisirs"
        "</div>",
        unsafe_allow_html=True,
    )