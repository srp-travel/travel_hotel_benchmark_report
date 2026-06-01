"""
pagination.py — Tableau paginé avec filtres (date, nuits, N/A).
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from config.constants import PAGE_SIZES, ROW_COLORS
from core.normalizer import fmt_ecart, fmt_price


# Format par défaut — utilisé si aucun format_map n'est passé
_DEFAULT_FORMAT: dict[str, Any] = {
    "Ecart PCT":          "{:.1%}",
    "Ecart EUR":          fmt_ecart,
    "Prix BKG (min)":     fmt_price,
    "Prix ORX / chambre": fmt_price,
    "Prix de vente TTC":  fmt_price,
}


def render_paginated_table(
    df_display:     pd.DataFrame,
    df_full:        pd.DataFrame,
    page_key:       str,
    page_size_key:  str,
    format_map:     dict[str, Any] | None = None,
) -> None:
    """
    Affiche le tableau de résultats avec :
      - filtres : masquer N/A, date de départ, nb nuits
      - pagination configurable
      - coloration conditionnelle par ligne
      - format_map optionnel (enrichi dynamiquement si décote Genius active)
    """
    effective_format = {**_DEFAULT_FORMAT, **(format_map or {})}

    # ── Filtres ────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 2, 2])

    with fc1:
        hide_na = st.checkbox(
            "Masquer les lignes sans comparaison BKG (N/A)",
            value=False,
            key="filter_hide_na",
        )
    with fc2:
        if "Date de départ" in df_display.columns:
            raw_dates = df_display["Date de départ"].replace("", pd.NA).dropna().unique().tolist()
            sorted_dates = sorted(
                raw_dates,
                key=lambda d: pd.to_datetime(d, format="%d/%m/%Y", errors="coerce"),
            )
            date_options: list[str] = ["Toutes"] + sorted_dates
        else:
            date_options = ["Toutes"]
        selected_date = st.selectbox("Filtrer par date de départ", date_options, key="filter_date")

    with fc3:
        nuits_raw = (
            sorted(df_display["Nb nuits"].dropna().unique().tolist())
            if "Nb nuits" in df_display.columns
            else []
        )
        nuits_options: list[str] = ["Toutes"] + [str(int(n)) for n in nuits_raw]
        selected_nuits = st.selectbox("Filtrer par nb nuits", nuits_options, key="filter_nuits")

    # ── Application des filtres ────────────────────────────────
    mask = pd.Series([True] * len(df_display), index=df_display.index)
    if hide_na:
        mask &= df_full["_competitivite"] != "N/A"
    if selected_date != "Toutes" and "Date de départ" in df_display.columns:
        mask &= df_display["Date de départ"] == selected_date
    if selected_nuits != "Toutes" and "Nb nuits" in df_display.columns:
        try:
            nuits_val = int(selected_nuits)
            mask &= df_display["Nb nuits"].astype(float).astype(int) == nuits_val
        except (ValueError, TypeError):
            pass

    df_view      = df_display[mask]
    df_view_full = df_full[mask]
    n_rows       = len(df_view)

    # ── Contrôle de page ───────────────────────────────────────
    ps_col, _, info_col = st.columns([2, 4, 2])
    with ps_col:
        page_size = st.selectbox("Lignes par page", PAGE_SIZES, index=1, key=page_size_key)
    with info_col:
        st.markdown(
            f"<div style='padding-top:28px;text-align:right;font-size:14px;color:#666;'>"
            f"{n_rows:,} ligne(s)</div>",
            unsafe_allow_html=True,
        )

    n_pages = max(1, (n_rows - 1) // page_size + 1)
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    if st.session_state[page_key] >= n_pages:
        st.session_state[page_key] = 0

    btn1, btn2, btn3 = st.columns([1, 4, 1])
    with btn1:
        if st.button("← Préc.", key=f"{page_key}_prev",
                     disabled=st.session_state[page_key] == 0):
            st.session_state[page_key] -= 1
            st.rerun()
    with btn2:
        st.markdown(
            f'<div class="pagination-bar">'
            f'Page <b>{st.session_state[page_key] + 1}</b> / <b>{n_pages}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with btn3:
        if st.button("Suiv. →", key=f"{page_key}_next",
                     disabled=st.session_state[page_key] == n_pages - 1):
            st.session_state[page_key] += 1
            st.rerun()

    # ── Affichage de la page courante ──────────────────────────
    start     = st.session_state[page_key] * page_size
    end       = start + page_size
    df_page   = df_view.iloc[start:end]
    df_p_full = df_view_full.iloc[start:end]

    # Applique uniquement les colonnes présentes dans df_page
    active_format = {k: v for k, v in effective_format.items() if k in df_page.columns}

    def style_row(row: pd.Series) -> list[str]:  # type: ignore[type-arg]
        comp  = df_p_full.at[row.name, "_competitivite"]
        color = ROW_COLORS.get(str(comp), ("", ""))[1]
        return [f"background-color: {color}" if color else ""] * len(row)

    st.dataframe(
        df_page.style.apply(style_row, axis=1).format(active_format),
        use_container_width=True,
        hide_index=True,
        height=min(52 + page_size * 36, 720),
    )