"""
data_loader.py — Lecture, validation et cache du fichier Excel source.

Comportement pandas par défaut (à éviter) :
  pd.read_excel() interprète de nombreuses chaînes comme NaN, dont "NA".
  Or le scraper écrit explicitement "NA" dans Meal Plan quand aucune
  pension n'est détectée. Ce "NA" disparaissait donc de safe_unique()
  (qui appelle .dropna()) et du multiselect de mapping.

Solution :
  keep_default_na=False  →  désactive la liste des NA par défaut de pandas.
  na_values=_REAL_NA     →  liste blanche explicite de ce qui doit rester NaN.
  "NA" n'est PAS dans _REAL_NA → conservé comme chaîne.

Note stubs Pylance :
  Les stubs pandas (Pylance >= 2026.2.1, _base.pyi Overload 4) ne déclarent
  pas keep_default_na dans tous leurs overloads → faux positif reportCallIssue.
  Suppression ciblée via # type: ignore[call-overload] sur les deux appels.
"""

from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from config.constants import SHEET_BKG, SHEET_ORX

# ── Valeurs qui doivent rester interprétées comme NaN ─────────────────────────
# Liste basée sur les defaults pandas, SANS "NA" (intentionnellement exclu).
_REAL_NA: list[str] = [
    "",          # cellule vide
    "#N/A",      # formule Excel d'erreur
    "#NA",       # variante Excel
    "N/A",       # "not available" — différent de "NA" logement seul
    "NULL",
    "null",
    "NaN",
    "nan",
    "-NaN",
    "-nan",
    "<NA>",
    "None",
    "1.#IND",
    "1.#QNAN",
    "-1.#IND",
    "-1.#QNAN",
]


@st.cache_data(show_spinner="Lecture du fichier...")
def load_data(file_bytes: bytes) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Charge les deux feuilles obligatoires du fichier Excel.
    Lève ValueError si une feuille est absente.

    keep_default_na=False + na_values=_REAL_NA :
      - Empêche pandas de convertir "NA" en NaN (correction bug Meal Plan BKG).
      - Conserve le comportement NaN pour les vraies cellules vides / erreurs Excel.

    Retour : (df_orx, df_bkg)
    """
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    missing = [s for s in [SHEET_ORX, SHEET_BKG] if s not in xls.sheet_names]
    if missing:
        raise ValueError(f"Feuilles manquantes : {', '.join(missing)}")

    # type: ignore[call-overload] — faux positif Pylance 2026.2.1 :
    # keep_default_na est absent de l'Overload 4 des stubs _base.pyi,
    # mais le paramètre existe bien dans pandas >= 1.0 et fonctionne à l'exécution.
    df_o: pd.DataFrame = pd.read_excel(  # type: ignore[call-overload]
        xls,
        sheet_name=SHEET_ORX,
        keep_default_na=False,
        na_values=_REAL_NA,
    )
    df_b: pd.DataFrame = pd.read_excel(  # type: ignore[call-overload]
        xls,
        sheet_name=SHEET_BKG,
        keep_default_na=False,
        na_values=_REAL_NA,
    )

    # Nettoyage des en-têtes
    df_o.columns = df_o.columns.str.strip()
    df_b.columns = df_b.columns.str.strip()

    return df_o, df_b


def safe_unique(df: pd.DataFrame, col: str) -> list[str]:
    """
    Retourne les valeurs uniques triées d'une colonne, sans lever d'erreur si absente.
    Grâce à keep_default_na=False dans load_data(), "NA" est désormais inclus
    comme valeur de chaîne normale et apparaît ici correctement.
    """
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).str.strip().unique().tolist())