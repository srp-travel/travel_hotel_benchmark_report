"""
data_loader.py — Lecture, validation et cache du fichier Excel source.
Aucune dépendance Streamlit directe sauf le décorateur @st.cache_data.
"""

from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from config.constants import SHEET_ORX, SHEET_BKG


@st.cache_data(show_spinner="Lecture du fichier...")
def load_data(file_bytes: bytes) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Charge les deux feuilles obligatoires du fichier Excel.
    Lève ValueError si une feuille est absente.
    Retour : (df_orx, df_bkg)
    """
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    missing = [s for s in [SHEET_ORX, SHEET_BKG] if s not in xls.sheet_names]
    if missing:
        raise ValueError(f"Feuilles manquantes : {', '.join(missing)}")

    df_o = pd.read_excel(xls, sheet_name=SHEET_ORX)
    df_b = pd.read_excel(xls, sheet_name=SHEET_BKG)

    # Nettoyage des en-têtes
    df_o.columns = df_o.columns.str.strip()
    df_b.columns = df_b.columns.str.strip()

    return df_o, df_b


def safe_unique(df: pd.DataFrame, col: str) -> list[str]:
    """Retourne les valeurs uniques triées d'une colonne, sans lever d'erreur si absente."""
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).str.strip().unique().tolist())
