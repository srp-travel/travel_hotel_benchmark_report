"""
tab_report.py — Onglet 5 : Génération et affichage du rapport de compétitivité.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.excel_exporter import build_excel
from core.matcher import run_matching
from core.normalizer import build_reverse_maps, fmt_ecart, fmt_price
from core.scoring import build_bench_header
from ui.components import (
    kpi,
    render_coverage_block,
    render_legend,
    render_seuil_stats,
    step_title,
)
from ui.pagination import render_paginated_table


def render(
    df_orx:         pd.DataFrame,
    df_bkg:         pd.DataFrame,
    room_mapping:   dict[str, list[str]],
    pension_config: dict[str, dict[str, list[str]]],
    cancel_config:  dict[str, dict[str, list[str]]],
    params:         dict[str, float],
    file_bytes:     bytes,
) -> None:
    step_title(5, "Rapport de compétitivité")

    missing_cats = [c for c, v in room_mapping.items() if not v]
    if missing_cats:
        st.warning(f"⚠️ Catégories sans mapping chambre : **{', '.join(missing_cats)}**")

    st.markdown("")
    ref_policy: str = st.session_state.get("ref_policy", "RF - Remboursable")
    genius_decote: float = params.get("genius_decote", 0.0)

    if st.button("🚀 Générer le rapport", type="primary", use_container_width=True):
        orx_pension_rev, bkg_meal_rev, bkg_cancel_rev = build_reverse_maps(
            pension_config, cancel_config
        )
        with st.spinner("Traitement en cours..."):
            df_result, n_no_map, n_no_bkg = run_matching(
                df_orx, df_bkg,
                room_mapping,
                orx_pension_rev, bkg_meal_rev, bkg_cancel_rev,
                ref_policy, params,
            )
        st.session_state["df_rapport"]  = df_result
        st.session_state["n_no_map"]    = n_no_map
        st.session_state["n_no_bkg"]    = n_no_bkg
        st.session_state["file_bytes"]  = file_bytes
        st.session_state["genius_decote"] = genius_decote

    if "df_rapport" not in st.session_state:
        st.info("Cliquez sur **Générer le rapport** pour lancer l'analyse.")
        return

    # ── Récupération des données ───────────────────────────────
    df    : pd.DataFrame = st.session_state["df_rapport"]
    n_nm  : int          = st.session_state["n_no_map"]
    n_nb  : int          = st.session_state["n_no_bkg"]
    used_genius: float   = st.session_state.get("genius_decote", 0.0)
    has_genius           = used_genius > 0
    prix_compare_col     = "Prix BKG Genius" if has_genius else "Prix BKG (min)"

    # ── Bandeau Genius (si décote active) ──────────────────────
    if has_genius:
        st.info(
            f"🎯 **Décote Genius active : {used_genius:.0%}** — "
            f"Les écarts sont calculés sur **Prix BKG Genius** "
            f"(prix brut × {1 - used_genius:.0%}). "
            f"La colonne **Prix BKG (min)** affiche le tarif scraped original."
        )

    df_comp   = df[df[prix_compare_col].notna() & df["Ecart EUR"].notna()] if has_genius \
                else df[df["Prix BKG (min)"].notna() & df["Ecart EUR"].notna()]
    df_scored    = df[df["_competitivite"] != "N/A"]
    n_total      = len(df)
    n_reussie    = len(df_comp)
    n_comparable = len(df_scored)
    taux         = n_reussie / n_total if n_total else 0.0

    hotel_name, date_range, nuits_str = build_bench_header(df)
    st.markdown("---")
    st.markdown(
        f'<div class="bench-title">Synthèse de bench — {hotel_name}</div>'
        f'<div class="bench-subtitle">'
        f'Date de départ : {date_range} &nbsp;|&nbsp; Nuitées : {nuits_str}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── KPIs ──────────────────────────────────────────────────
    sc1, sc2, sc3 = st.columns(3, gap="medium")

    with sc1:
        st.markdown('<div class="kpi-section-title">Positionnement Orchestra</div>', unsafe_allow_html=True)
        if not df_scored.empty:
            render_seuil_stats(df_scored, n_comparable)
            st.markdown(
                f"<div style='font-size:13px;color:#666;margin-top:7px;'>"
                f"Sur {n_comparable:,} comparaison(s) avec seuil calculé</div>",
                unsafe_allow_html=True,
            )
        else:
            st.caption("Aucune comparaison disponible.")

    with sc2:
        st.markdown('<div class="kpi-section-title">Analyse des écarts</div>', unsafe_allow_html=True)
        if not df_comp.empty:
            def cls_e(v: float) -> str:
                return "success" if v < 0 else "danger" if v > 0 else ""
            kpi("Ecart moyen (EUR)",   f"{df_comp['Ecart EUR'].mean():+,.0f} EUR", cls_e(float(df_comp['Ecart EUR'].mean())))
            kpi("Ecart moyen (%)",     f"{df_comp['Ecart PCT'].mean():+.1%}",      cls_e(float(df_comp['Ecart PCT'].mean())))
            kpi("Ecart maximum (EUR)", f"{df_comp['Ecart EUR'].max():+,.0f} EUR",  cls_e(float(df_comp['Ecart EUR'].max())))
            kpi("Ecart minimum (EUR)", f"{df_comp['Ecart EUR'].min():+,.0f} EUR",  cls_e(float(df_comp['Ecart EUR'].min())))
        else:
            st.caption("Aucune comparaison disponible.")

    with sc3:
        st.markdown('<div class="kpi-section-title">Indicateurs généraux</div>', unsafe_allow_html=True)
        kpi("Nombre total de lignes",       f"{n_total:,}")
        kpi("Comparaisons réussies",         f"{n_reussie:,}")
        kpi("Taux de comparaisons réussies", f"{taux:.0%}",
            "success" if taux >= 0.5 else "warning" if taux > 0 else "danger")
        kpi("Lignes sans mapping chambre",   f"{n_nm:,}", "warning" if n_nm > 0 else "")
        kpi("Lignes sans prix BKG",          f"{n_nb:,}", "warning" if n_nb > 0 else "")
        if has_genius:
            kpi("Décote Genius appliquée", f"{used_genius:.0%}", "success")

    st.markdown("")
    render_coverage_block(df)

    st.markdown("---")
    render_legend()

    # Colonnes d'affichage : on retire Hotel et _competitivite
    df_display = df.drop(columns=["_competitivite", "Hotel"])

    # Formatage dynamique selon présence colonne Genius
    format_map: dict[str, object] = {
        "Ecart PCT":          "{:.1%}",
        "Ecart EUR":          fmt_ecart,
        "Prix BKG (min)":     fmt_price,
        "Prix ORX / chambre": fmt_price,
        "Prix de vente TTC":  fmt_price,
    }
    if has_genius:
        format_map["Prix BKG Genius"] = fmt_price

    render_paginated_table(df_display, df, "report_page", "report_page_size", format_map)

    st.markdown("")
    excel_bytes = build_excel(df_display, st.session_state["file_bytes"], df)
    st.download_button(
        label="⬇️  Télécharger le rapport Excel",
        data=excel_bytes,
        file_name="benchmark_rapport.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )