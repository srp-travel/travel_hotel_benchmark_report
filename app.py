#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║      Benchmark Tarifaire ORX vs Booking.com  —  Interface UI    ║
╠══════════════════════════════════════════════════════════════════╣
║  Prérequis :  pip install streamlit pandas openpyxl              ║
║  Lancement :  streamlit run benchmark_ui.py                      ║
╚══════════════════════════════════════════════════════════════════╝
"""

import io
import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ══════════════════════════════════════════════════════════════════
# CONSTANTES — Vocabulaire normalisé (valeurs fixes)
# ══════════════════════════════════════════════════════════════════

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
    "✅ Très compétitif": "C6EFCE",
    "✅ Compétitif":       "E2EFDA",
    "⚠️ Proche":           "FFEB9C",
    "❌ Non compétitif":   "FFC7CE",
    "N/A":                 "F2F2F2",
}

COL_WIDTHS = {
    "Date de départ":             16,
    "Nb nuits":                   10,
    "Pension ORX (norm.)":        24,
    "Catégorie ORX":              20,
    "Prix de vente TTC":          18,
    "Type de prix":               14,
    "Room Type BKG":              38,
    "Meal Plan BKG":              38,
    "Politique annulation BKG":   45,
    "Prix BKG (min)":             16,
    "Écart €":                    13,
    "Écart %":                    13,
    "Compétitivité":              22,
}


# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Benchmark Tarifaire",
    page_icon="🏨",
    layout="wide",
)

st.title("🏨 Benchmark Tarifaire — ORX vs Booking.com")
st.markdown("---")


# ══════════════════════════════════════════════════════════════════
# ÉTAPE 1 — CHARGEMENT DU FICHIER
# ══════════════════════════════════════════════════════════════════

st.header("📂 Chargement du fichier")

uploaded = st.file_uploader(
    label="Fichier Excel (.xlsx) — doit contenir les feuilles **1. INPUT ORX EXPORT** et **2. OUTPUT BKG SCRAP**",
    type=["xlsx"],
)

if not uploaded:
    st.info("👆 Chargez un fichier Excel pour commencer.")
    st.stop()


# ── Lecture des deux feuilles ─────────────────────────────────────
@st.cache_data(show_spinner="Lecture du fichier…")
def load_data(file_bytes: bytes):
    xls = pd.ExcelFile(io.BytesIO(file_bytes))

    available = xls.sheet_names
    required  = ["1. INPUT ORX EXPORT", "2. OUTPUT BKG SCRAP"]
    missing   = [s for s in required if s not in available]
    if missing:
        raise ValueError(f"Feuilles manquantes dans le fichier : {missing}")

    df_orx = pd.read_excel(xls, sheet_name="1. INPUT ORX EXPORT")
    df_bkg = pd.read_excel(xls, sheet_name="2. OUTPUT BKG SCRAP")
    df_orx.columns = df_orx.columns.str.strip()
    df_bkg.columns = df_bkg.columns.str.strip()
    return df_orx, df_bkg


file_bytes = uploaded.read()

try:
    df_orx, df_bkg = load_data(file_bytes)
except ValueError as e:
    st.error(str(e))
    st.stop()

# Valeurs uniques détectées automatiquement
orx_categories   = sorted(df_orx["Catégorie"].dropna().astype(str).unique())
orx_pensions_raw = sorted(df_orx["Pension"].dropna().astype(str).unique())
bkg_room_types   = sorted(df_bkg["Room Type"].dropna().astype(str).unique())
bkg_cancel_raw   = sorted(df_bkg["Cancellation Policy"].dropna().astype(str).unique())

col1, col2 = st.columns(2)
col1.success(f"✅ **ORX** : {len(df_orx)} lignes — {len(orx_categories)} catégories")
col2.success(f"✅ **BKG** : {len(df_bkg)} lignes — {len(bkg_room_types)} types de chambres")

st.markdown("---")


# ══════════════════════════════════════════════════════════════════
# ONGLETS DE CONFIGURATION
# ══════════════════════════════════════════════════════════════════

tab_rooms, tab_pensions, tab_cancel, tab_params, tab_report = st.tabs([
    "🛏️  Types de chambres",
    "🍽️  Pensions",
    "📋  Annulation",
    "⚙️  Paramètres",
    "📊  Rapport",
])


# ══════════════════════════════════════════════════════════════════
# ONGLET 1 — MAPPING TYPES DE CHAMBRES
# ══════════════════════════════════════════════════════════════════

with tab_rooms:
    st.subheader("🛏️ Catégories ORX  →  Types de chambres Booking")
    st.caption(
        "Pour chaque catégorie ORX détectée dans le fichier, "
        "sélectionnez les types de chambres Booking correspondants. "
        "Vous pouvez en associer plusieurs."
    )
    st.markdown("")

    room_mapping: dict[str, list[str]] = {}

    for cat in orx_categories:
        room_mapping[cat] = st.multiselect(
            label=f"**{cat}**",
            options=bkg_room_types,
            key=f"room__{cat}",
            placeholder="Sélectionnez un ou plusieurs types de chambre BKG…",
        )

    # Aperçu du mapping saisi
    preview_rows = [
        {"Catégorie ORX": cat, "Room Type BKG": rt}
        for cat, rts in room_mapping.items()
        for rt in rts
    ]
    if preview_rows:
        st.markdown("---")
        st.markdown("**Aperçu du mapping :**")
        st.dataframe(pd.DataFrame(preview_rows), hide_index=True, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# ONGLET 2 — MAPPING PENSIONS
# ══════════════════════════════════════════════════════════════════

with tab_pensions:
    st.subheader("🍽️ Libellés de pension ORX  →  Valeur normalisée")
    st.caption(
        "Chaque libellé brut détecté dans la colonne **Pension** du fichier ORX "
        "doit être associé à une valeur du vocabulaire normalisé ci-dessous."
    )

    # Référentiel affiché pour aide
    with st.expander("📖 Référentiel des pensions normalisées"):
        st.dataframe(
            pd.DataFrame({"Code": PENSIONS_NORM}),
            hide_index=True, use_container_width=True,
        )

    st.markdown("")
    pension_mapping: dict[str, str] = {}

    for raw in orx_pensions_raw:
        selected = st.selectbox(
            label=f"**{raw}**",
            options=["— Non mappé —"] + PENSIONS_NORM,
            key=f"pension__{raw}",
        )
        if selected != "— Non mappé —":
            pension_mapping[raw] = selected


# ══════════════════════════════════════════════════════════════════
# ONGLET 3 — MAPPING POLITIQUES D'ANNULATION
# ══════════════════════════════════════════════════════════════════

with tab_cancel:
    st.subheader("📋 Politiques d'annulation BKG  →  Valeur normalisée")
    st.caption(
        "Chaque libellé brut détecté dans la colonne **Cancellation Policy** du fichier BKG "
        "doit être associé à une valeur du vocabulaire normalisé ci-dessous."
    )

    with st.expander("📖 Référentiel des politiques d'annulation normalisées"):
        st.dataframe(
            pd.DataFrame({"Code": ANNULATIONS_NORM}),
            hide_index=True, use_container_width=True,
        )

    st.markdown("")
    cancel_mapping: dict[str, str] = {}

    for raw in bkg_cancel_raw:
        selected = st.selectbox(
            label=f"**{raw}**",
            options=["— Non mappé —"] + ANNULATIONS_NORM,
            key=f"cancel__{raw}",
        )
        if selected != "— Non mappé —":
            cancel_mapping[raw] = selected


# ══════════════════════════════════════════════════════════════════
# ONGLET 4 — PARAMÈTRES DE BENCHMARK
# ══════════════════════════════════════════════════════════════════

with tab_params:
    st.subheader("⚙️ Paramètres de benchmark")
    st.markdown("")

    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown("**Politique d'annulation de référence**")
        ref_policy = st.selectbox(
            label="Politique de référence",
            options=ANNULATIONS_NORM,
            index=ANNULATIONS_NORM.index("RF - Remboursable"),
            label_visibility="collapsed",
            help="Politique utilisée comme référence pour les comparaisons.",
        )

    with col_b:
        st.markdown("**Seuils de compétitivité** *(écart en %)*")

        seuil_proche = st.number_input(
            "Seuil Proche / Non compétitif",
            value=-10, min_value=-99, max_value=0, step=1, format="%d",
            help="Au-delà de ce seuil (ex : -10%), le prix est jugé 'Non compétitif'.",
        ) / 100

        seuil_competitif = st.number_input(
            "Seuil Compétitif",
            value=-15, min_value=-99, max_value=0, step=1, format="%d",
        ) / 100

        seuil_tres_competitif = st.number_input(
            "Seuil Très compétitif",
            value=-20, min_value=-99, max_value=0, step=1, format="%d",
        ) / 100

    # Récapitulatif visuel
    st.markdown("---")
    st.markdown("**Récapitulatif des indicateurs :**")
    st.dataframe(pd.DataFrame([
        {"Indicateur": "❌ Non compétitif",  "Condition": f"Écart > {int(seuil_proche*100)}%"},
        {"Indicateur": "⚠️ Proche",          "Condition": f"{int(seuil_competitif*100)}% < Écart ≤ {int(seuil_proche*100)}%"},
        {"Indicateur": "✅ Compétitif",       "Condition": f"{int(seuil_tres_competitif*100)}% < Écart ≤ {int(seuil_competitif*100)}%"},
        {"Indicateur": "✅ Très compétitif",  "Condition": f"Écart ≤ {int(seuil_tres_competitif*100)}%"},
    ]), hide_index=True, use_container_width=True)

    params = {
        "ref_policy":            ref_policy,
        "seuil_non_competitif":  seuil_proche,
        "seuil_competitif":      seuil_competitif,
        "seuil_tres_competitif": seuil_tres_competitif,
    }


# ══════════════════════════════════════════════════════════════════
# ONGLET 5 — GÉNÉRATION DU RAPPORT
# ══════════════════════════════════════════════════════════════════

with tab_report:
    st.subheader("📊 Génération du rapport")

    # ── Validation des mappings ───────────────────────────────────
    warnings = []
    missing_rooms    = [c for c, v in room_mapping.items() if not v]
    missing_pensions = [p for p in orx_pensions_raw if p not in pension_mapping]

    if missing_rooms:
        warnings.append(f"⚠️ Catégories sans mapping chambre : **{', '.join(missing_rooms)}**")
    if missing_pensions:
        warnings.append(f"⚠️ Pensions sans mapping : **{', '.join(missing_pensions)}**")

    for w in warnings:
        st.warning(w)

    st.markdown("")
    generate = st.button("🚀 Générer le rapport", type="primary", use_container_width=True)

    if generate:

        # ── Traitement métier ─────────────────────────────────────
        def normalize_price(val):
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str):
                try:
                    return float(val.replace(" ", "").replace(",", "."))
                except ValueError:
                    return None
            return None

        def get_competitiveness(pct):
            if pct is None:
                return ""
            if pct <= params["seuil_tres_competitif"]:
                return "✅ Très compétitif"
            if pct <= params["seuil_competitif"]:
                return "✅ Compétitif"
            if pct <= params["seuil_non_competitif"]:
                return "⚠️ Proche"
            return "❌ Non compétitif"

        with st.spinner("Calcul en cours…"):
            df_orx_p = df_orx.copy()
            df_bkg_p = df_bkg.copy()
            df_orx_p["Date de départ"] = pd.to_datetime(df_orx_p["Date de départ"]).dt.date
            df_bkg_p["Check-in"]       = pd.to_datetime(df_bkg_p["Check-in"]).dt.date

            results = []
            for _, orx_row in df_orx_p.iterrows():
                date_dep         = orx_row["Date de départ"]
                categorie        = str(orx_row.get("Catégorie", "")).strip()
                pension_raw      = str(orx_row.get("Pension", "")).strip()
                pension_norm     = pension_mapping.get(pension_raw, f"⚠️ Non mappé : {pension_raw}")
                prix_ttc_raw     = orx_row.get("Prix de vente TTC")
                prix_orx_num     = normalize_price(prix_ttc_raw)
                prix_orx_chambre = prix_orx_num * 2 if prix_orx_num is not None else None
                room_types       = room_mapping.get(categorie, [])

                bkg_matches = df_bkg_p[
                    (df_bkg_p["Check-in"] == date_dep) &
                    (df_bkg_p["Room Type"].isin(room_types))
                ]

                if bkg_matches.empty:
                    bkg_room = bkg_meal = bkg_cancel = "N/A"
                    prix_bkg = ecart_eur = ecart_pct = None
                    competitivite = "N/A"
                else:
                    cheapest      = bkg_matches.loc[bkg_matches["Price"].idxmin()]
                    bkg_room      = str(cheapest["Room Type"])
                    bkg_meal      = str(cheapest["Meal Plan"])
                    bkg_cancel    = str(cheapest["Cancellation Policy"])
                    prix_bkg      = float(cheapest["Price"])
                    if prix_orx_chambre and prix_bkg:
                        ecart_eur     = round(prix_orx_chambre - prix_bkg, 2)
                        ecart_pct     = round((prix_orx_chambre - prix_bkg) / prix_bkg, 4)
                        competitivite = get_competitiveness(ecart_pct)
                    else:
                        ecart_eur = ecart_pct = None
                        competitivite = ""

                results.append({
                    "Date de départ":            date_dep,
                    "Nb nuits":                  orx_row.get("Nb nuits"),
                    "Pension ORX (norm.)":       pension_norm,
                    "Catégorie ORX":             categorie,
                    "Prix de vente TTC":         prix_ttc_raw,
                    "Type de prix":              orx_row.get("Type de prix"),
                    "Room Type BKG":             bkg_room,
                    "Meal Plan BKG":             bkg_meal,
                    "Politique annulation BKG":  bkg_cancel,
                    "Prix BKG (min)":            prix_bkg,
                    "Écart €":                   ecart_eur,
                    "Écart %":                   ecart_pct,
                    "Compétitivité":             competitivite,
                })

            df_rapport = pd.DataFrame(results)

        # ── Métriques résumé ──────────────────────────────────────
        st.success(f"✅ {len(df_rapport)} lignes traitées")
        counts = df_rapport["Compétitivité"].value_counts()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("✅ Très compétitif", counts.get("✅ Très compétitif", 0))
        m2.metric("✅ Compétitif",      counts.get("✅ Compétitif",      0))
        m3.metric("⚠️ Proche",          counts.get("⚠️ Proche",          0))
        m4.metric("❌ Non compétitif",   counts.get("❌ Non compétitif",  0))

        # ── Tableau coloré ────────────────────────────────────────
        color_map = {
            "✅ Très compétitif": "background-color: #C6EFCE",
            "✅ Compétitif":       "background-color: #E2EFDA",
            "⚠️ Proche":           "background-color: #FFEB9C",
            "❌ Non compétitif":   "background-color: #FFC7CE",
            "N/A":                 "background-color: #F2F2F2",
        }

        def style_row(row):
            color = color_map.get(str(row.get("Compétitivité", "")), "")
            return [color] * len(row)

        st.dataframe(
            df_rapport.style
                .apply(style_row, axis=1)
                .format({"Écart %": "{:.2%}", "Écart €": "{:.2f} €", "Prix BKG (min)": "{:.2f} €"},
                        na_rep=""),
            use_container_width=True,
            hide_index=True,
        )

        # ── Export Excel ──────────────────────────────────────────
        output_buffer = io.BytesIO()
        wb_out = openpyxl.load_workbook(io.BytesIO(file_bytes))

        sheet_name = "4. RAPPORT DÉTAILLÉ"
        if sheet_name in wb_out.sheetnames:
            del wb_out[sheet_name]
        ws = wb_out.create_sheet(sheet_name)

        headers = list(df_rapport.columns)

        # En-têtes
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font      = Font(bold=True, color="FFFFFF", size=10)
            cell.fill      = PatternFill("solid", fgColor="1F3864")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws.column_dimensions[get_column_letter(col_idx)].width = COL_WIDTHS.get(header, 18)
        ws.row_dimensions[1].height = 30

        # Lignes de données
        for row_idx, (_, row_data) in enumerate(df_rapport.iterrows(), 2):
            competitivite = str(row_data.get("Compétitivité", ""))
            fill_color    = ROW_COLORS.get(competitivite)
            fill          = PatternFill("solid", fgColor=fill_color) if fill_color else None
            border        = Border(
                bottom=Side(style="thin", color="D0D0D0"),
                right=Side(style="thin",  color="D0D0D0"),
            )

            for col_idx, header in enumerate(headers, 1):
                val  = row_data[header]
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font   = Font(size=10)
                cell.border = border

                is_empty = val is None or (not isinstance(val, str) and pd.isna(val))

                if is_empty:
                    cell.value = None
                elif header == "Écart %" and isinstance(val, (int, float)):
                    cell.value         = val
                    cell.number_format = "0.00%"
                    cell.alignment     = Alignment(horizontal="right")
                elif header in ("Écart €", "Prix BKG (min)") and isinstance(val, (int, float)):
                    cell.value         = val
                    cell.number_format = '#,##0.00 "€"'
                    cell.alignment     = Alignment(horizontal="right")
                elif header == "Date de départ":
                    cell.value         = val
                    cell.number_format = "DD/MM/YYYY"
                    cell.alignment     = Alignment(horizontal="center")
                elif header == "Nb nuits":
                    cell.value     = val
                    cell.alignment = Alignment(horizontal="center")
                else:
                    cell.value = val

                if fill:
                    cell.fill = fill

        ws.freeze_panes = "A2"
        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

        wb_out.save(output_buffer)
        output_buffer.seek(0)

        st.markdown("")
        st.download_button(
            label="⬇️ Télécharger le rapport Excel",
            data=output_buffer,
            file_name="benchmark_rapport.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )
