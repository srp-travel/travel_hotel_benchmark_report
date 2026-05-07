#!/usr/bin/env python3
"""
Benchmark Tarifaire ORX vs Booking.com
Usage : streamlit run benchmark_ui.py
Prérequis : pip install streamlit pandas openpyxl
"""

import io
import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ══════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════

PENSIONS_NORM = [
    "PDJ - Petit-déjeuner",
    "DP - Demi-pension",
    "PC - Pension complète",
    "TI - Tout inclus",
    "LS - Logement seul",
]

ANNULATIONS_NORM = [
    "AG - Annulation gratuite",
    "NA - Non annulable",
    "NANR - Non annulable / Non remboursable",
    "NR - Non remboursable",
    "PR - Partiellement remboursable",
    "RF - Remboursable",
]

ROW_COLORS = {
    "✅ Très compétitif": ("C6EFCE", "#C6EFCE"),
    "✅ Compétitif":       ("E2EFDA", "#E2EFDA"),
    "⚠️ Proche":           ("FFEB9C", "#FFEB9C"),
    "❌ Non compétitif":   ("FFC7CE", "#FFC7CE"),
    "N/A":                 ("F2F2F2", "#F2F2F2"),
}

COL_WIDTHS = {
    "Hotel":                            30,
    "Travel Window":                    18,
    "Nb nuits":                         10,
    "Catégorie ORX":                    22,
    "Pension ORX (norm.)":              24,
    "Type de prix":                     14,
    "Prix de vente TTC":                18,
    "Prix ORX / chambre":               18,
    "Room Type BKG":                    40,
    "Meal Plan BKG":                    36,
    "Meal Plan BKG (norm.)":            26,
    "Politique annulation BKG (norm.)": 38,
    "Prix BKG (min)":                   16,
    "Ecart EUR":                        13,
    "Ecart PCT":                        13,
}

PAGE_SIZES = [10, 25, 50, 100]


# ══════════════════════════════════════════════════════════════
# PAGE & CSS
# ══════════════════════════════════════════════════════════════

st.set_page_config(page_title="Benchmark Tarifaire", page_icon="🏨", layout="wide")

st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; max-width: 1400px; }
    .step-title {
        display: flex; align-items: center; gap: 10px;
        font-size: 17px; font-weight: 600; color: #1F3864;
        margin: 0 0 6px 0;
    }
    .step-badge {
        display: inline-flex; align-items: center; justify-content: center;
        min-width: 26px; height: 26px;
        background: #1F3864; color: white;
        border-radius: 50%; font-size: 13px; font-weight: 700;
    }
    .kpi-section-title {
        font-size: 12px; font-weight: 700; text-transform: uppercase;
        letter-spacing: .06em; color: #1F3864;
        border-bottom: 2px solid #1F3864;
        padding-bottom: 4px; margin: 14px 0 10px 0;
    }
    .kpi-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 5px 0; border-bottom: 1px solid #F0F0F0;
    }
    .kpi-label  { font-size: 13px; color: #444; }
    .kpi-value  { font-size: 14px; font-weight: 600; color: #1F3864; }
    .kpi-value.danger  { color: #C00000; }
    .kpi-value.warning { color: #9C6500; }
    .kpi-value.success { color: #375623; }
    .tw-bar-wrap {
        background: #E8E8E8; border-radius: 20px; height: 14px;
        overflow: hidden; margin: 6px 0 2px 0;
    }
    .tw-bar-fill { height: 100%; border-radius: 20px; transition: width .4s; }
    .legend-wrap  { display: flex; gap: 18px; flex-wrap: wrap; margin: 8px 0 12px 0; align-items: center; }
    .legend-item  { display: flex; align-items: center; gap: 6px; font-size: 13px; }
    .legend-dot   { width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; border: 1px solid #ccc; }
    .pagination-bar {
        display: flex; align-items: center; justify-content: center;
        gap: 12px; padding: 8px 0; font-size: 14px; color: #1F3864;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 18px; border-radius: 5px 5px 0 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🏨 Benchmark Tarifaire")
st.caption("Analyse de compétitivité tarifaire — ORX (Orchestra) vs Booking.com")
st.markdown("---")


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def safe_unique(df, col):
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).str.strip().unique().tolist())


def normalize_price(val):
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val.replace(" ", "").replace("\u202f", "").replace(",", "."))
        except ValueError:
            return None
    return None


def get_competitiveness(pct, params):
    if pct is None:
        return "N/A"
    if pct <= params["seuil_tres_competitif"]:
        return "✅ Très compétitif"
    if pct <= params["seuil_competitif"]:
        return "✅ Compétitif"
    if pct <= params["seuil_non_competitif"]:
        return "⚠️ Proche"
    return "❌ Non compétitif"


def build_reverse_maps(pension_config, cancel_config):
    orx_pension_rev = {v: n for n, vals in pension_config.items() for v in vals.get("orx", [])}
    bkg_meal_rev    = {v: n for n, vals in pension_config.items() for v in vals.get("bkg", [])}
    bkg_cancel_rev  = {v: n for n, vals in cancel_config.items()  for v in vals.get("bkg", [])}
    return orx_pension_rev, bkg_meal_rev, bkg_cancel_rev


def compute_travel_window_coverage(df):
    tw_cols     = ["Travel Window", "Nb nuits"]
    all_windows = df[tw_cols].drop_duplicates().copy()
    all_windows["_has_bkg"] = all_windows.apply(
        lambda r: df[
            (df["Travel Window"] == r["Travel Window"]) &
            (df["Nb nuits"]      == r["Nb nuits"]) &
            (df["Prix BKG (min)"].notna())
        ].shape[0] > 0,
        axis=1,
    )
    n_total   = len(all_windows)
    n_covered = int(all_windows["_has_bkg"].sum())
    rate      = n_covered / n_total if n_total else 0
    return {
        "total":   n_total,
        "covered": n_covered,
        "missing": n_total - n_covered,
        "rate":    rate,
        "detail":  all_windows.sort_values(tw_cols),
    }


def step_title(n, label):
    st.markdown(
        f'<div class="step-title"><span class="step-badge">{n}</span>{label}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")


def kpi(label, value, cls=""):
    st.markdown(
        f'<div class="kpi-row"><span class="kpi-label">{label}</span>'
        f'<span class="kpi-value {cls}">{value}</span></div>',
        unsafe_allow_html=True,
    )


def render_paginated_table(df_display, df_full, page_key, page_size_key):
    """Tableau filtrable et paginé. Prix affichés sans décimales."""

    # ── Filtres ──────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 2, 2])
    with fc1:
        hide_na = st.checkbox(
            "Masquer les lignes sans comparaison BKG (N/A)",
            value=False, key="filter_hide_na",
        )
    with fc2:
        hotel_options = ["Tous"] + sorted(df_display["Hotel"].dropna().unique().tolist()) \
            if "Hotel" in df_display.columns else ["Tous"]
        selected_hotel = st.selectbox("Filtrer par hôtel", hotel_options, key="filter_hotel")
    with fc3:
        tw_options = ["Toutes"] + sorted(df_display["Travel Window"].dropna().unique().tolist()) \
            if "Travel Window" in df_display.columns else ["Toutes"]
        selected_tw = st.selectbox("Filtrer par Travel Window", tw_options, key="filter_tw")

    # ── Application des filtres ───────────────────────────────
    mask = pd.Series([True] * len(df_display), index=df_display.index)
    if hide_na:
        mask &= df_full["_competitivite"] != "N/A"
    if selected_hotel != "Tous" and "Hotel" in df_display.columns:
        mask &= df_display["Hotel"] == selected_hotel
    if selected_tw != "Toutes" and "Travel Window" in df_display.columns:
        mask &= df_display["Travel Window"] == selected_tw

    df_view      = df_display[mask]
    df_view_full = df_full[mask]
    n_rows       = len(df_view)

    # ── Pagination ────────────────────────────────────────────
    ps_col, _, info_col = st.columns([2, 4, 2])
    with ps_col:
        page_size = st.selectbox("Lignes par page", PAGE_SIZES, index=1, key=page_size_key)
    with info_col:
        st.markdown(
            f"<div style='padding-top:28px;text-align:right;font-size:13px;color:#666;'>"
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

    start     = st.session_state[page_key] * page_size
    end       = start + page_size
    df_page   = df_view.iloc[start:end]
    df_p_full = df_view_full.iloc[start:end]

    def style_row(row):
        comp  = df_p_full.at[row.name, "_competitivite"]
        color = ROW_COLORS.get(comp, ("", ""))[1]
        return [f"background-color: {color}" if color else ""] * len(row)

    # Prix affiches sans decimales
    st.dataframe(
        df_page.style.apply(style_row, axis=1).format(
            {
                "Ecart PCT":          "{:.1%}",
                "Ecart EUR":          "{:+,.0f}",
                "Prix BKG (min)":     "{:,.0f}",
                "Prix ORX / chambre": "{:,.0f}",
                "Prix de vente TTC":  "{:,.0f}",
            },
            na_rep="—",
        ),
        use_container_width=True,
        hide_index=True,
        height=min(52 + page_size * 35, 700),
    )


@st.cache_data(show_spinner="Lecture du fichier...")
def load_data(file_bytes):
    xls      = pd.ExcelFile(io.BytesIO(file_bytes))
    required = ["1. INPUT ORX EXPORT", "2. OUTPUT BKG SCRAP"]
    missing  = [s for s in required if s not in xls.sheet_names]
    if missing:
        raise ValueError(f"Feuilles manquantes : {', '.join(missing)}")
    df_o = pd.read_excel(xls, sheet_name="1. INPUT ORX EXPORT")
    df_b = pd.read_excel(xls, sheet_name="2. OUTPUT BKG SCRAP")
    df_o.columns = df_o.columns.str.strip()
    df_b.columns = df_b.columns.str.strip()
    return df_o, df_b


# ══════════════════════════════════════════════════════════════
# ÉTAPE 0 — CHARGEMENT
# ══════════════════════════════════════════════════════════════

step_title(0, "Chargement du fichier Excel")

uploaded = st.file_uploader(
    "Fichier .xlsx — feuilles attendues : 1. INPUT ORX EXPORT  |  2. OUTPUT BKG SCRAP",
    type=["xlsx"],
)

if uploaded is None:
    st.info("👆 Chargez votre fichier Excel pour démarrer la configuration.")

else:
    file_bytes = uploaded.read()

    try:
        df_orx, df_bkg = load_data(file_bytes)
    except Exception as e:
        st.error(f"❌ Erreur de lecture : {e}")

    else:
        # Nom de l'hotel = 1ere colonne de la feuille BKG
        bkg_hotel_col = df_bkg.columns[0]

        orx_categories     = safe_unique(df_orx, "Catégorie")
        orx_pensions_raw   = safe_unique(df_orx, "Pension")
        bkg_room_types     = safe_unique(df_bkg, "Room Type")
        bkg_meal_plans_raw = safe_unique(df_bkg, "Meal Plan")
        bkg_cancel_raw     = safe_unique(df_bkg, "Cancellation Policy")

        c1, c2 = st.columns(2)
        c1.success(f"✅ ORX — {len(df_orx):,} lignes · {len(orx_categories)} catégorie(s) · {len(orx_pensions_raw)} libellé(s) pension")
        c2.success(f"✅ BKG — {len(df_bkg):,} lignes · {len(bkg_room_types)} type(s) de chambre · {len(bkg_cancel_raw)} politique(s) d'annulation")
        st.caption(f"🏨 Colonne hôtel (BKG col. 1) : **{bkg_hotel_col}**")
        st.markdown("---")

        tab_params, tab_rooms, tab_pensions, tab_cancel, tab_report = st.tabs([
            "⚙️  1 · Paramètres",
            "🛏️  2 · Chambres",
            "🍽️  3 · Pensions",
            "📋  4 · Annulation",
            "📊  5 · Rapport",
        ])

        # ── ONGLET 1 ──────────────────────────────────────────
        with tab_params:
            step_title(1, "Paramètres de benchmark")
            col_a, col_b = st.columns([1, 1], gap="large")
            with col_a:
                st.markdown("**Politique d'annulation de référence**")
                ref_policy = st.selectbox(
                    "ref_policy", options=ANNULATIONS_NORM,
                    index=ANNULATIONS_NORM.index("RF - Remboursable"),
                    label_visibility="collapsed",
                )
                st.info(f"Référence : **{ref_policy}**")
            with col_b:
                st.markdown("**Seuils de compétitivité** *(valeurs négatives en %)*")
                st.caption("Ecart = (Prix ORX - Prix BKG) / Prix BKG")
                seuil_proche = st.number_input(
                    "Seuil Non compétitif / Proche",
                    value=-10, min_value=-99, max_value=0, step=1, format="%d",
                ) / 100
                seuil_competitif = st.number_input(
                    "Seuil Proche / Compétitif",
                    value=-15, min_value=-99, max_value=0, step=1, format="%d",
                ) / 100
                seuil_tres_competitif = st.number_input(
                    "Seuil Compétitif / Très compétitif",
                    value=-20, min_value=-99, max_value=0, step=1, format="%d",
                ) / 100
            st.markdown("---")
            st.dataframe(pd.DataFrame([
                {"Indicateur": "❌ Non compétitif",  "Condition": f"Ecart > {int(seuil_proche*100)}%"},
                {"Indicateur": "⚠️ Proche",          "Condition": f"{int(seuil_competitif*100)}% < Ecart <= {int(seuil_proche*100)}%"},
                {"Indicateur": "✅ Compétitif",       "Condition": f"{int(seuil_tres_competitif*100)}% < Ecart <= {int(seuil_competitif*100)}%"},
                {"Indicateur": "✅ Très compétitif",  "Condition": f"Ecart <= {int(seuil_tres_competitif*100)}%"},
            ]), hide_index=True, use_container_width=True)
            params = {
                "ref_policy":            ref_policy,
                "seuil_non_competitif":  seuil_proche,
                "seuil_competitif":      seuil_competitif,
                "seuil_tres_competitif": seuil_tres_competitif,
            }

        # ── ONGLET 2 ──────────────────────────────────────────
        with tab_rooms:
            step_title(2, "Mapping — Types de chambres")
            st.caption("Pour chaque catégorie ORX, associez un ou plusieurs types de chambres Booking.")
            st.markdown("")
            room_mapping = {}
            for cat in orx_categories:
                room_mapping[cat] = st.multiselect(
                    label=f"**{cat}**",
                    options=bkg_room_types,
                    key=f"room__{cat}",
                    placeholder="Types de chambre BKG correspondants...",
                )
            preview = [{"Catégorie ORX": c, "Room Type BKG": rt}
                       for c, rts in room_mapping.items() for rt in rts]
            if preview:
                st.markdown("---")
                st.dataframe(pd.DataFrame(preview), hide_index=True, use_container_width=True)
            else:
                st.warning("⚠️ Aucun mapping chambre défini — toutes les lignes seront N/A.")

        # ── ONGLET 3 ──────────────────────────────────────────
        with tab_pensions:
            step_title(3, "Mapping — Pensions / Meal Plans")
            st.markdown("")
            pension_config = {}
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
            orx_p_rev, bkg_m_rev, _ = build_reverse_maps(pension_config, {})
            unmapped_orx_p = [v for v in orx_pensions_raw   if v not in orx_p_rev]
            unmapped_bkg_m = [v for v in bkg_meal_plans_raw if v not in bkg_m_rev]
            if unmapped_orx_p:
                st.warning(f"⚠️ Libellés ORX non mappés : {', '.join(unmapped_orx_p)}")
            if unmapped_bkg_m:
                st.warning(f"⚠️ Libellés BKG non mappés : {', '.join(unmapped_bkg_m)}")

        # ── ONGLET 4 ──────────────────────────────────────────
        with tab_cancel:
            step_title(4, "Mapping — Politiques d'annulation")
            st.markdown("")
            cancel_config = {}
            for norm in ANNULATIONS_NORM:
                with st.expander(f"📋  **{norm}**", expanded=False):
                    st.markdown("**Sources BKG** *(colonne : Cancellation Policy)*")
                    bkg_cancel_vals = st.multiselect(
                        "bkg", options=bkg_cancel_raw, key=f"c_bkg__{norm}",
                        label_visibility="collapsed", placeholder="Libellés BKG...",
                    )
                    cancel_config[norm] = {"bkg": bkg_cancel_vals}
            _, _, bkg_c_rev = build_reverse_maps(pension_config, cancel_config)
            unmapped_bkg_c = [v for v in bkg_cancel_raw if v not in bkg_c_rev]
            if unmapped_bkg_c:
                st.warning(f"⚠️ Politiques BKG non mappées : {', '.join(unmapped_bkg_c)}")

        # ── ONGLET 5 ──────────────────────────────────────────
        with tab_report:
            step_title(5, "Rapport de compétitivité")
            missing_room_cats = [c for c, v in room_mapping.items() if not v]
            if missing_room_cats:
                st.warning(f"⚠️ Catégories sans mapping chambre : **{', '.join(missing_room_cats)}**")
            st.markdown("")
            generate_btn = st.button("🚀 Générer le rapport", type="primary", use_container_width=True)

            if generate_btn:
                orx_pension_rev, bkg_meal_rev, bkg_cancel_rev = build_reverse_maps(pension_config, cancel_config)
                with st.spinner("Traitement en cours..."):
                    df_orx_p = df_orx.copy()
                    df_bkg_p = df_bkg.copy()
                    df_orx_p["Date de départ"] = pd.to_datetime(df_orx_p["Date de départ"], errors="coerce").dt.date
                    df_bkg_p["Check-in"]       = pd.to_datetime(df_bkg_p["Check-in"],       errors="coerce").dt.date

                    results  = []
                    n_no_map = 0
                    n_no_bkg = 0

                    for _, orx_row in df_orx_p.iterrows():
                        date_dep    = orx_row.get("Date de départ")
                        nb_nuits    = orx_row.get("Nb nuits")
                        categorie   = str(orx_row.get("Catégorie", "")).strip()
                        pension_raw = str(orx_row.get("Pension", "")).strip()

                        try:
                            tw_label = date_dep.strftime("%d/%m/%Y") if date_dep else ""
                        except Exception:
                            tw_label = str(date_dep) if date_dep else ""

                        pension_norm     = orx_pension_rev.get(pension_raw, f"Non mappé : {pension_raw}")
                        prix_ttc_raw     = orx_row.get("Prix de vente TTC")
                        prix_orx_num     = normalize_price(prix_ttc_raw)
                        prix_orx_chambre = round(prix_orx_num * 2, 2) if prix_orx_num is not None else None
                        room_types       = room_mapping.get(categorie, [])

                        if not room_types:
                            n_no_map += 1
                            nom_hotel = ""
                            bkg_room = bkg_meal = bkg_meal_norm = bkg_cancel_norm = "N/A"
                            prix_bkg = ecart_eur = ecart_pct = None
                            competitivite = "N/A"
                        else:
                            bkg_matches = df_bkg_p[
                                (df_bkg_p["Check-in"] == date_dep) &
                                (df_bkg_p["Room Type"].isin(room_types))
                            ]
                            if bkg_matches.empty:
                                n_no_bkg += 1
                                nom_hotel = ""
                                bkg_room = bkg_meal = bkg_meal_norm = bkg_cancel_norm = "N/A"
                                prix_bkg = ecart_eur = ecart_pct = None
                                competitivite = "N/A"
                            else:
                                cheapest = bkg_matches.loc[bkg_matches["Price"].idxmin()]
                                # Nom hotel depuis la 1ere colonne de la feuille BKG
                                nom_hotel      = str(cheapest.get(bkg_hotel_col, "")).strip()
                                bkg_room       = str(cheapest.get("Room Type", ""))
                                bkg_meal       = str(cheapest.get("Meal Plan", ""))
                                bkg_meal_norm  = bkg_meal_rev.get(bkg_meal, f"Non mappé : {bkg_meal}")
                                bkg_cancel_raw_val = str(cheapest.get("Cancellation Policy", ""))
                                bkg_cancel_norm    = bkg_cancel_rev.get(bkg_cancel_raw_val, f"Non mappé : {bkg_cancel_raw_val}")
                                prix_bkg       = float(cheapest["Price"])
                                if prix_orx_chambre and prix_bkg:
                                    ecart_eur     = round(prix_orx_chambre - prix_bkg, 2)
                                    ecart_pct     = round((prix_orx_chambre - prix_bkg) / prix_bkg, 4)
                                    competitivite = get_competitiveness(ecart_pct, params)
                                else:
                                    ecart_eur = ecart_pct = None
                                    competitivite = "N/A"

                        results.append({
                            "Hotel":                            nom_hotel,
                            "Travel Window":                    tw_label,
                            "Nb nuits":                         nb_nuits,
                            "Catégorie ORX":                    categorie,
                            "Pension ORX (norm.)":              pension_norm,
                            "Type de prix":                     orx_row.get("Type de prix"),
                            "Prix de vente TTC":                prix_ttc_raw,
                            "Prix ORX / chambre":               prix_orx_chambre,
                            "Room Type BKG":                    bkg_room,
                            "Meal Plan BKG":                    bkg_meal,
                            "Meal Plan BKG (norm.)":            bkg_meal_norm,
                            "Politique annulation BKG (norm.)": bkg_cancel_norm,
                            "Prix BKG (min)":                   prix_bkg,
                            "Ecart EUR":                        ecart_eur,
                            "Ecart PCT":                        ecart_pct,
                            "_competitivite":                   competitivite,
                        })

                    st.session_state["df_rapport"] = pd.DataFrame(results)
                    st.session_state["n_no_map"]   = n_no_map
                    st.session_state["n_no_bkg"]   = n_no_bkg
                    st.session_state["file_bytes"] = file_bytes

            if "df_rapport" not in st.session_state:
                st.info("Cliquez sur **Générer le rapport** pour lancer l'analyse.")
            else:
                df   = st.session_state["df_rapport"]
                n_nm = st.session_state["n_no_map"]
                n_nb = st.session_state["n_no_bkg"]

                df_comp   = df[df["Prix BKG (min)"].notna() & df["Ecart EUR"].notna()]
                n_total   = len(df)
                n_reussie = len(df_comp)
                taux      = n_reussie / n_total if n_total else 0

                st.markdown("---")
                st.markdown("### Synthèse")
                sc1, sc2, sc3 = st.columns(3, gap="medium")

                with sc1:
                    st.markdown('<div class="kpi-section-title">Indicateurs généraux</div>', unsafe_allow_html=True)
                    kpi("Nombre total de lignes",        f"{n_total:,}")
                    kpi("Comparaisons réussies",          f"{n_reussie:,}")
                    kpi("Taux de comparaisons réussies",  f"{taux:.0%}",
                        "success" if taux >= 0.5 else "warning" if taux > 0 else "danger")
                    kpi("Lignes sans mapping chambre",    f"{n_nm:,}", "warning" if n_nm > 0 else "")
                    kpi("Lignes sans prix BKG",           f"{n_nb:,}", "warning" if n_nb > 0 else "")

                with sc2:
                    st.markdown('<div class="kpi-section-title">Analyse des écarts</div>', unsafe_allow_html=True)
                    if not df_comp.empty:
                        def cls_e(v):
                            return "success" if v < 0 else "danger" if v > 0 else ""
                        kpi("Ecart moyen (EUR)",   f"{df_comp['Ecart EUR'].mean():+,.0f} EUR", cls_e(df_comp['Ecart EUR'].mean()))
                        kpi("Ecart moyen (%)",     f"{df_comp['Ecart PCT'].mean():+.1%}",      cls_e(df_comp['Ecart PCT'].mean()))
                        kpi("Ecart maximum (EUR)", f"{df_comp['Ecart EUR'].max():+,.0f} EUR",  cls_e(df_comp['Ecart EUR'].max()))
                        kpi("Ecart minimum (EUR)", f"{df_comp['Ecart EUR'].min():+,.0f} EUR",  cls_e(df_comp['Ecart EUR'].min()))
                    else:
                        st.caption("Aucune comparaison disponible.")

                with sc3:
                    st.markdown('<div class="kpi-section-title">Positionnement Orchestra</div>', unsafe_allow_html=True)
                    if not df_comp.empty:
                        n_moins = int((df_comp["Ecart EUR"] < 0).sum())
                        n_plus  = int((df_comp["Ecart EUR"] > 0).sum())
                        n_egaux = int((df_comp["Ecart EUR"] == 0).sum())
                        pct_m   = n_moins / n_reussie if n_reussie else 0
                        kpi("ORX moins cher",   f"{n_moins:,}", "success")
                        kpi("ORX plus cher",    f"{n_plus:,}",  "danger" if n_plus > 0 else "")
                        kpi("Prix égaux",       f"{n_egaux:,}")
                        kpi("% ORX moins cher", f"{pct_m:.1%}",
                            "success" if pct_m >= 0.5 else "warning" if pct_m > 0.2 else "danger")
                    else:
                        st.caption("Aucune comparaison disponible.")

                # ── COUVERTURE TRAVEL WINDOW ──────────────────
                st.markdown("")
                tw        = compute_travel_window_coverage(df)
                bar_color = "#375623" if tw["rate"] >= 0.8 else "#9C6500" if tw["rate"] >= 0.4 else "#C00000"
                bar_w     = int(tw["rate"] * 100)

                with st.container(border=True):
                    st.markdown('<div class="kpi-section-title">Couverture de la Travel Window</div>', unsafe_allow_html=True)
                    st.caption("Pour chaque combinaison unique (Travel Window x Nb nuits), vérifie si au moins une correspondance BKG existe.")
                    tw1, tw2, tw3 = st.columns(3)
                    tw1.metric("Fenêtres tarifaires (total)",  f"{tw['total']:,}")
                    tw2.metric("Avec correspondance BKG",      f"{tw['covered']:,}")
                    tw3.metric("Sans correspondance",          f"{tw['missing']:,}",
                               delta=f"-{tw['missing']}" if tw["missing"] > 0 else None,
                               delta_color="inverse")
                    st.markdown(
                        f'<div style="margin:8px 0 4px 0;font-size:13px;font-weight:600;color:{bar_color};">'
                        f'Taux de couverture : {tw["rate"]:.1%}</div>'
                        f'<div class="tw-bar-wrap"><div class="tw-bar-fill" '
                        f'style="width:{bar_w}%;background:{bar_color};"></div></div>',
                        unsafe_allow_html=True,
                    )
                    with st.expander("Détail par fenêtre tarifaire", expanded=False):
                        detail = tw["detail"].copy()
                        detail["Statut"] = detail["_has_bkg"].map({True: "✅ Couverte", False: "❌ Manquante"})
                        st.dataframe(
                            detail[["Travel Window", "Nb nuits", "Statut"]],
                            hide_index=True, use_container_width=True,
                        )

                # ── LÉGENDE ───────────────────────────────────
                st.markdown("---")
                legend_items = [
                    ("#C6EFCE", "Très compétitif"), ("#E2EFDA", "Compétitif"),
                    ("#FFEB9C", "Proche"),           ("#FFC7CE", "Non compétitif"),
                    ("#F2F2F2", "N/A"),
                ]
                st.markdown(
                    '<div class="legend-wrap">' +
                    "".join(
                        f'<div class="legend-item">'
                        f'<div class="legend-dot" style="background:{c};"></div>{l}'
                        f'</div>'
                        for c, l in legend_items
                    ) + "</div>",
                    unsafe_allow_html=True,
                )

                # ── TABLEAU PAGINÉ ────────────────────────────
                df_display = df.drop(columns=["_competitivite"])
                render_paginated_table(df_display, df, "report_page", "report_page_size")

                # ── EXPORT EXCEL ──────────────────────────────
                st.markdown("")

                def build_excel(df_out, orig_bytes):
                    wb = openpyxl.load_workbook(io.BytesIO(orig_bytes))
                    sn = "4. RAPPORT DETAILLE"
                    if sn in wb.sheetnames:
                        del wb[sn]
                    ws       = wb.create_sheet(sn)
                    headers  = list(df_out.columns)
                    hdr_fill = PatternFill("solid", fgColor="1F3864")
                    hdr_font = Font(bold=True, color="FFFFFF", size=10)
                    thin_bdr = Border(
                        bottom=Side(style="thin", color="D0D0D0"),
                        right=Side(style="thin",  color="D0D0D0"),
                    )
                    for ci, h in enumerate(headers, 1):
                        cell = ws.cell(row=1, column=ci, value=h)
                        cell.font, cell.fill = hdr_font, hdr_fill
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        ws.column_dimensions[get_column_letter(ci)].width = COL_WIDTHS.get(h, 18)
                    ws.row_dimensions[1].height = 30

                    for ri, (orig_idx, row_data) in enumerate(df_out.iterrows(), 2):
                        comp     = df.at[orig_idx, "_competitivite"]
                        row_fill = PatternFill("solid", fgColor=ROW_COLORS.get(comp, ("F2F2F2",))[0])
                        for ci, h in enumerate(headers, 1):
                            val  = row_data[h]
                            cell = ws.cell(row=ri, column=ci)
                            cell.font, cell.border, cell.fill = Font(size=10), thin_bdr, row_fill
                            is_nan = val is None or (not isinstance(val, str) and pd.isna(val))
                            if is_nan:
                                cell.value = None
                            elif h == "Ecart PCT" and isinstance(val, (int, float)):
                                # Pourcentage avec 1 decimale
                                cell.value, cell.number_format = val, "0.0%"
                                cell.alignment = Alignment(horizontal="right")
                            elif h in ("Ecart EUR", "Prix BKG (min)", "Prix ORX / chambre", "Prix de vente TTC") \
                                    and isinstance(val, (int, float)):
                                # Prix sans decimales
                                cell.value, cell.number_format = val, '#,##0 "EUR"'
                                cell.alignment = Alignment(horizontal="right")
                            elif h in ("Travel Window", "Nb nuits"):
                                cell.value     = val
                                cell.alignment = Alignment(horizontal="center")
                            else:
                                cell.value = val

                    ws.freeze_panes = "A2"
                    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"
                    buf = io.BytesIO()
                    wb.save(buf)
                    buf.seek(0)
                    return buf.read()

                excel_bytes = build_excel(df_display, st.session_state["file_bytes"])

                st.download_button(
                    label="Télécharger le rapport Excel",
                    data=excel_bytes,
                    file_name="benchmark_rapport.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                )