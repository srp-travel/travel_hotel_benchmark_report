"""
scoring.py — Calcul des niveaux de compétitivité et de la couverture des dates.
Aucune dépendance Streamlit.
"""

from __future__ import annotations

import pandas as pd


def get_competitiveness(pct: float | None, params: dict[str, float]) -> str:
    """
    Retourne le label de compétitivité selon l'écart en % et les seuils configurés.
    Seuils attendus dans params :
      - seuil_tres_competitif  (ex. -0.20)
      - seuil_competitif       (ex. -0.15)
      - seuil_non_competitif   (ex. -0.10)
    """
    if pct is None:
        return "N/A"
    if pct <= params["seuil_tres_competitif"]:
        return "✅ Très compétitif"
    if pct <= params["seuil_competitif"]:
        return "✅ Compétitif"
    if pct <= params["seuil_non_competitif"]:
        return "⚠️ Proche"
    return "❌ Non compétitif"


def compute_date_coverage(df: pd.DataFrame) -> dict[str, object]:
    """
    Analyse la couverture BKG par combinaison (Date de départ x Nb nuits).
    Retourne un dict avec total, covered, missing, rate, detail.
    Complexité O(n) via set de lookup.
    """
    key_cols    = ["Date de départ", "Nb nuits"]
    all_windows = df[key_cols].drop_duplicates().copy()

    covered_keys: set[tuple[object, object]] = set(
        zip(
            df.loc[df["Prix BKG (min)"].notna(), "Date de départ"],
            df.loc[df["Prix BKG (min)"].notna(), "Nb nuits"],
        )
    )
    all_windows["_has_bkg"] = [
        (d, n) in covered_keys
        for d, n in zip(all_windows["Date de départ"], all_windows["Nb nuits"])
    ]

    n_total   = len(all_windows)
    n_covered = int(all_windows["_has_bkg"].sum())
    rate      = n_covered / n_total if n_total else 0.0

    return {
        "total":   n_total,
        "covered": n_covered,
        "missing": n_total - n_covered,
        "rate":    rate,
        "detail":  all_windows.sort_values(key_cols),
    }


def build_bench_header(df: pd.DataFrame) -> tuple[str, str, str]:
    """Extrait nom d'hôtel, plage de dates et liste de nuitées depuis le rapport."""
    hotel_vals = df["Hotel"].replace("", pd.NA).dropna().unique()
    hotel_name = str(hotel_vals[0]) if len(hotel_vals) > 0 else "Hôtel inconnu"

    dates_parsed = pd.to_datetime(
        df["Date de départ"], format="%d/%m/%Y", errors="coerce"
    ).dropna()

    if not dates_parsed.empty:
        date_min   = dates_parsed.min().strftime("%d/%m/%Y")
        date_max   = dates_parsed.max().strftime("%d/%m/%Y")
        date_range = f"{date_min} → {date_max}" if date_min != date_max else date_min
    else:
        date_range = "—"

    nuits = sorted([int(n) for n in df["Nb nuits"].dropna().unique()])
    if not nuits:
        nuits_str = "—"
    elif len(nuits) == 1:
        nuits_str = str(nuits[0])
    else:
        nuits_str = ", ".join(str(n) for n in nuits[:-1]) + " et " + str(nuits[-1])

    return hotel_name, date_range, nuits_str
