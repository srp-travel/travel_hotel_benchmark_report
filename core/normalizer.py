"""
normalizer.py — Fonctions de normalisation des données brutes.
Aucune dépendance Streamlit. Testable unitairement.
"""

from __future__ import annotations

import pandas as pd


# ── Accès sécurisé aux Series ──────────────────────────────────────────────────

def row_get(row: pd.Series, key: str, default: object = None) -> object:
    """Accès sécurisé à une valeur de Series, gère NaN/None/KeyError."""
    try:
        val = row[key]
        if val is None:
            return default
        try:
            return default if pd.isna(val) else val  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return val
    except KeyError:
        return default


def scalar(row: pd.Series, key: str, default: str = "") -> str:
    try:
        val = row[key]
        return default if pd.isna(val) else str(val)  # type: ignore[arg-type]
    except (KeyError, TypeError):
        return default


def get_float(row: pd.Series, key: str) -> float | None:
    try:
        val = row[key]
        return None if pd.isna(val) else float(val)  # type: ignore[arg-type]
    except (KeyError, TypeError, ValueError):
        return None


# ── Normalisation du prix ──────────────────────────────────────────────────────

def normalize_price(val: object) -> float | None:
    """Convertit une valeur brute (str avec espaces, virgules) en float."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val.replace(" ", "").replace("\u202f", "").replace(",", "."))
        except ValueError:
            return None
    return None


def _type_de_prix_str(type_de_prix: object) -> str:
    """
    Convertit la valeur brute de 'Type de prix' en chaîne normalisée.
    Gère tous les cas pathologiques issus de pandas :
      - None, pd.NA, pd.NaT   → ""
      - float("nan")          → ""
      - int/float (1, 1.0)    → "1", "1.0"
      - str ("1*", "2 pers")  → "1*", "2 pers"
    """
    if type_de_prix is None:
        return ""
    try:
        if pd.isna(type_de_prix):  # type: ignore[arg-type]
            return ""
    except (TypeError, ValueError):
        pass  # pd.isna peut lever TypeError sur certains types custom
    return str(type_de_prix).strip()


def orx_price_per_room(prix_ttc_raw: object, type_de_prix: object) -> float | None:
    """
    Convertit le prix ORX en prix par chambre (base 2 personnes).

    Règle :
      Type commence par "1"  (ex. "1*", "1 pers", 1, 1.0) → prix par personne → × 2
      Tout autre cas                                        → prix par chambre → × 1

    Le guard _type_de_prix_str() gère None, NaN, pd.NA et les valeurs numériques
    lues par pandas depuis Excel (int 1 → "1", float 1.0 → "1.0").
    """
    prix = normalize_price(prix_ttc_raw)
    if prix is None:
        return None
    type_str = _type_de_prix_str(type_de_prix)
    return round(prix * 2, 2) if type_str.startswith("1") else prix


# ── Reverse maps (libellé brut → valeur normalisée) ───────────────────────────

def build_reverse_maps(
    pension_config: dict[str, dict[str, list[str]]],
    cancel_config:  dict[str, dict[str, list[str]]],
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """
    Construit 3 dicts de lookup :
      - orx_pension_rev : libellé brut ORX → valeur normalisée pension
      - bkg_meal_rev    : libellé brut BKG → valeur normalisée pension
      - bkg_cancel_rev  : libellé brut BKG → valeur normalisée annulation
    """
    orx_pension_rev = {v: n for n, vals in pension_config.items() for v in vals.get("orx", [])}
    bkg_meal_rev    = {v: n for n, vals in pension_config.items() for v in vals.get("bkg", [])}
    bkg_cancel_rev  = {v: n for n, vals in cancel_config.items()  for v in vals.get("bkg", [])}
    return orx_pension_rev, bkg_meal_rev, bkg_cancel_rev


# ── Formatage affichage ────────────────────────────────────────────────────────

def fmt_price(v: object) -> str:
    if v is None or (not isinstance(v, str) and pd.isna(v)):  # type: ignore[arg-type]
        return "—"
    f = float(v)  # type: ignore[arg-type]
    return f"{f:,.0f}" if f == int(f) else f"{f:,.2f}"


def fmt_ecart(v: object) -> str:
    if v is None or (not isinstance(v, str) and pd.isna(v)):  # type: ignore[arg-type]
        return "—"
    f = float(v)  # type: ignore[arg-type]
    return f"{f:+,.0f}" if f == int(f) else f"{f:+,.2f}"