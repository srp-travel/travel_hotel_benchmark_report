"""
matcher.py — Construction de l'index BKG et matching ORX↔BKG.
Logique O(1) par lookup via dict pré-indexé.
Aucune dépendance Streamlit.
"""

from __future__ import annotations

import pandas as pd

from core.normalizer import row_get, scalar, get_float, orx_price_per_room


# Type alias pour l'index BKG
BkgIndex = dict[tuple[object, str, str], pd.Series]


def build_bkg_index(df_bkg: pd.DataFrame, bkg_meal_rev: dict[str, str]) -> BkgIndex:
    """
    Pré-calcule un index (date, meal_norm, room_type) → ligne BKG au prix minimum.
    Complexité : O(n log n) une seule fois, puis O(1) par lookup.
    """
    df = df_bkg.copy()
    df["_meal_norm"] = (
        df["Meal Plan"].astype(str).str.strip()
        .map(lambda m: bkg_meal_rev.get(str(m), ""))
    )

    bkg_min = (
        df.sort_values("Price")
        .groupby(["Check-in", "_meal_norm", "Room Type"], as_index=False)
        .first()
    )

    return {
        (row["Check-in"], str(row["_meal_norm"]), str(row["Room Type"])): row
        for _, row in bkg_min.iterrows()
    }


def find_cheapest_bkg(
    bkg_index:    BkgIndex,
    date:         object,
    meal_norm:    str,
    room_types:   list[str],
) -> pd.Series | None:
    """
    Retourne la ligne BKG la moins chère pour la combinaison (date, meal_norm)
    parmi les room_types autorisés. Retourne None si aucune correspondance.
    """
    cheapest: pd.Series | None = None
    cheapest_price = float("inf")

    for rt in room_types:
        candidate = bkg_index.get((date, meal_norm, str(rt)))
        if candidate is not None:
            p = get_float(candidate, "Price")
            if p is not None and p < cheapest_price:
                cheapest_price = p
                cheapest = candidate

    return cheapest


def run_matching(
    df_orx:          pd.DataFrame,
    df_bkg:          pd.DataFrame,
    room_mapping:    dict[str, list[str]],
    orx_pension_rev: dict[str, str],
    bkg_meal_rev:    dict[str, str],
    bkg_cancel_rev:  dict[str, str],
    ref_policy:      str,
    params:          dict[str, float],
) -> tuple[pd.DataFrame, int, int]:
    """
    Exécute le matching complet ORX↔BKG et retourne :
      - df_result       : DataFrame avec colonnes affichage + _competitivite
      - n_no_map        : lignes sans mapping chambre
      - n_no_bkg        : lignes sans prix BKG trouvé
    """
    from core.scoring import get_competitiveness

    # -- Parsing dates
    df_orx_p = df_orx.copy()
    df_bkg_p = df_bkg.copy()
    df_orx_p["Date de départ"] = pd.to_datetime(
        df_orx_p["Date de départ"], errors="coerce"
    ).dt.date
    df_bkg_p["Check-in"] = pd.to_datetime(
        df_bkg_p["Check-in"], errors="coerce"
    ).dt.date

    bkg_hotel_col = str(df_bkg_p.columns[0])
    bkg_index     = build_bkg_index(df_bkg_p, bkg_meal_rev)

    results: list[dict[str, object]] = []
    n_no_map = 0
    n_no_bkg = 0

    for _, orx_row in df_orx_p.iterrows():
        date_dep    = row_get(orx_row, "Date de départ")
        nb_nuits    = row_get(orx_row, "Nb nuits")
        categorie   = str(row_get(orx_row, "Catégorie",   "") or "").strip()
        pension_raw = str(row_get(orx_row, "Pension",     "") or "").strip()

        pension_norm       = orx_pension_rev.get(pension_raw, f"Non mappé : {pension_raw}")
        pension_norm_valid = bool(pension_norm and not pension_norm.startswith("Non mappé"))

        try:
            date_label = date_dep.strftime("%d/%m/%Y") if date_dep else ""  # type: ignore[union-attr]
        except Exception:
            date_label = str(date_dep) if date_dep else ""

        prix_ttc_raw     = row_get(orx_row, "Prix de vente TTC")
        prix_orx_chambre = orx_price_per_room(prix_ttc_raw, row_get(orx_row, "Type de prix"))
        room_types       = room_mapping.get(categorie, [])

        if not room_types:
            n_no_map += 1
            nom_hotel = ""
            bkg_room = bkg_meal = bkg_meal_norm = bkg_cancel_norm = "N/A"
            prix_bkg: float | None  = None
            ecart_eur: float | None = None
            ecart_pct: float | None = None
            competitivite = "N/A"

        else:
            meal_key       = pension_norm if pension_norm_valid else ""
            cheapest_row   = find_cheapest_bkg(bkg_index, date_dep, meal_key, room_types)

            if cheapest_row is None:
                n_no_bkg += 1
                nom_hotel = ""
                bkg_room = bkg_meal = bkg_meal_norm = bkg_cancel_norm = "N/A"
                prix_bkg = ecart_eur = ecart_pct = None
                competitivite = "N/A"
            else:
                nom_hotel          = scalar(cheapest_row, bkg_hotel_col).strip()
                bkg_room           = scalar(cheapest_row, "Room Type")
                bkg_meal           = scalar(cheapest_row, "Meal Plan")
                bkg_meal_norm      = bkg_meal_rev.get(bkg_meal.strip(), f"Non mappé : {bkg_meal}")
                bkg_cancel_raw_val = scalar(cheapest_row, "Cancellation Policy")
                bkg_cancel_norm    = bkg_cancel_rev.get(
                    bkg_cancel_raw_val, f"Non mappé : {bkg_cancel_raw_val}"
                )
                prix_bkg = get_float(cheapest_row, "Price")

                if prix_orx_chambre is not None and prix_bkg is not None:
                    ecart_eur     = round(prix_orx_chambre - prix_bkg, 2)
                    ecart_pct     = round((prix_orx_chambre - prix_bkg) / prix_bkg, 4)
                    competitivite = get_competitiveness(ecart_pct, params)
                else:
                    ecart_eur = ecart_pct = None
                    competitivite = "N/A"

        results.append({
            "Hotel":                               nom_hotel,
            "Date de départ":                      date_label,
            "Nb nuits":                            nb_nuits,
            "Catégorie ORX":                       categorie,
            "Pension ORX (norm.)":                 pension_norm,
            "Politique annulation ORX (réf.)":     ref_policy,
            "Type de prix":                        row_get(orx_row, "Type de prix"),
            "Prix de vente TTC":                   prix_ttc_raw,
            "Prix ORX / chambre":                  prix_orx_chambre,
            "Room Type BKG":                       bkg_room,
            "Meal Plan BKG":                       bkg_meal,
            "Meal Plan BKG (norm.)":               bkg_meal_norm,
            "Politique annulation BKG (norm.)":    bkg_cancel_norm,
            "Prix BKG (min)":                      prix_bkg,
            "Ecart EUR":                           ecart_eur,
            "Ecart PCT":                           ecart_pct,
            "_competitivite":                      competitivite,
        })

    return pd.DataFrame(results), n_no_map, n_no_bkg
