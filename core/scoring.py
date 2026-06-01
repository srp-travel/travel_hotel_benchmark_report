
from __future__ import annotations

from typing import Any

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


def compute_raw_date_coverage(
    df_orx: pd.DataFrame,
    df_bkg: pd.DataFrame,
) -> dict[str, Any]:
    """
    Couverture BRUTE Travel Window : dates de départ ORX vs Check-in BKG,
    avant tout mapping chambre/pension.

    Répond à : "Le scraping BKG couvre-t-il les bonnes dates ?"

    Retourne un dict :
      - orx_total    : nb de dates uniques dans ORX
      - bkg_total    : nb de dates uniques dans BKG
      - covered      : nb de dates ORX présentes dans BKG
      - missing      : nb de dates ORX absentes de BKG
      - extra_bkg    : nb de dates BKG sans correspondance ORX
      - rate         : taux de couverture (covered / orx_total)
      - detail       : DataFrame (date, statut, nb_lignes_bkg)
      - missing_dates: liste des dates manquantes formatées jj/mm/aaaa
    """
    orx_dates_raw = pd.to_datetime(df_orx["Date de départ"], errors="coerce").dt.date
    bkg_dates_raw = pd.to_datetime(df_bkg["Check-in"],       errors="coerce").dt.date

    orx_unique = sorted(orx_dates_raw.dropna().unique())
    bkg_set    = set(bkg_dates_raw.dropna().unique())
    bkg_unique = sorted(bkg_set)

    # Compte du nb de lignes BKG par date (toutes chambres/pensions confondues)
    # Annotation Any pour éviter l'incompatibilité dict[Hashable, int] vs dict[object, int]
    bkg_counts: dict[Any, int] = bkg_dates_raw.dropna().value_counts().to_dict()

    covered   = [d for d in orx_unique if d in bkg_set]
    missing   = [d for d in orx_unique if d not in bkg_set]
    extra_bkg = [d for d in bkg_unique if d not in set(orx_unique)]

    n_total   = len(orx_unique)
    n_covered = len(covered)
    rate      = n_covered / n_total if n_total else 0.0

    detail = pd.DataFrame({
        "Date de départ ORX": [d.strftime("%d/%m/%Y") for d in orx_unique],
        "Statut": [
            "✅ Présente dans BKG" if d in bkg_set else "❌ Absente du BKG"
            for d in orx_unique
        ],
        "Nb lignes BKG dispo": [int(bkg_counts.get(d, 0)) for d in orx_unique],
    })

    return {
        "orx_total":     n_total,
        "bkg_total":     len(bkg_unique),
        "covered":       n_covered,
        "missing":       len(missing),
        "extra_bkg":     len(extra_bkg),
        "rate":          rate,
        "detail":        detail,
        "missing_dates": [d.strftime("%d/%m/%Y") for d in missing],
    }


def compute_date_coverage(df: pd.DataFrame) -> dict[str, Any]:
    """
    Couverture ENRICHIE (post-génération) : par combinaison (Date de départ x Nb nuits),
    vérifie si une correspondance BKG avec mapping complet (chambre + pension) existe.
    Complexité O(n) via set de lookup.
    """
    key_cols    = ["Date de départ", "Nb nuits"]
    all_windows = df[key_cols].drop_duplicates().copy()

    covered_keys: set[tuple[Any, Any]] = set(
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