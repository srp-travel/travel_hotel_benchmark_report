"""
constants.py — Toutes les constantes métier et UI de l'application.
Modifier uniquement ce fichier pour ajuster les labels, seuils par défaut et couleurs.
"""

# ── Valeurs normalisées ────────────────────────────────────────────────────────

PENSIONS_NORM: list[str] = [
    "PDJ - Petit-déjeuner",
    "DP - Demi-pension",
    "PC - Pension complète",
    "TI - Tout inclus",
    "LS - Logement seul",
]

ANNULATIONS_NORM: list[str] = [
    "AG - Annulation gratuite",
    "NA - Non annulable",
    "NANR - Non annulable / Non remboursable",
    "NR - Non remboursable",
    "PR - Partiellement remboursable",
    "RF - Remboursable",
]

# ── Compétitivité ──────────────────────────────────────────────────────────────
# (label, classe CSS Streamlit, couleur hex fond)
SEUIL_LABELS: list[tuple[str, str, str]] = [
    ("✅ Très compétitif", "success", "#C6EFCE"),
    ("✅ Compétitif",       "success", "#E2EFDA"),
    ("⚠️ Proche",           "warning", "#FFEB9C"),
    ("❌ Non compétitif",   "danger",  "#FFC7CE"),
]

# Seuils de compétitivité par défaut (modifiables dans l'onglet Paramètres)
DEFAULT_SEUIL_PROCHE:          int = -10   # %
DEFAULT_SEUIL_COMPETITIF:      int = -15   # %
DEFAULT_SEUIL_TRES_COMPETITIF: int = -20   # %

# Décote Genius par défaut — 0 = désactivée
DEFAULT_GENIUS_DECOTE: int = 0   # %

# ── Couleurs de fond par niveau (hex Excel, hex HTML) ─────────────────────────
ROW_COLORS: dict[str, tuple[str, str]] = {
    "✅ Très compétitif": ("C6EFCE", "#C6EFCE"),
    "✅ Compétitif":       ("E2EFDA", "#E2EFDA"),
    "⚠️ Proche":           ("FFEB9C", "#FFEB9C"),
    "❌ Non compétitif":   ("FFC7CE", "#FFC7CE"),
    "N/A":                 ("F2F2F2", "#F2F2F2"),
}

# ── Largeurs colonnes Excel (caractères) ──────────────────────────────────────
COL_WIDTHS: dict[str, int] = {
    "Date de départ":                      16,
    "Nb nuits":                            10,
    "Catégorie ORX":                       22,
    "Pension ORX (norm.)":                 24,
    "Politique annulation ORX (réf.)":     34,
    "Type de prix":                        14,
    "Prix de vente TTC":                   18,
    "Prix ORX / chambre":                  18,
    "Room Type BKG":                       40,
    "Meal Plan BKG":                       36,
    "Meal Plan BKG (norm.)":               26,
    "Politique annulation BKG (norm.)":    38,
    "Prix BKG (min)":                      16,
    "Prix BKG Genius":                     18,
    "Ecart EUR":                           13,
    "Ecart PCT":                           13,
}

# ── Pagination ─────────────────────────────────────────────────────────────────
PAGE_SIZES: list[int] = [10, 25, 50, 100]

# ── Feuilles Excel attendues ───────────────────────────────────────────────────
SHEET_ORX:    str = "1. INPUT ORX EXPORT"
SHEET_BKG:    str = "2. OUTPUT BKG SCRAP"
SHEET_REPORT: str = "4. RAPPORT DETAILLE"