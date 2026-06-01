# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.  
Format : [Semantic Versioning](https://semver.org/lang/fr/)

---

## [2.0.0] — 2026-06-01

### 🏗️ Refactorisation complète — Architecture modulaire

Réécriture totale du fichier `app.py` monolithique (~700 lignes) en une architecture
en couches séparées, sans modification du comportement métier existant.

**Avant :** 1 fichier, tout couplé  
**Après :** 14 modules organisés en `config/`, `core/`, `ui/`

```
config/constants.py          ← toutes les constantes en un seul endroit
core/data_loader.py          ← lecture Excel + cache
core/normalizer.py           ← normalisation prix, pensions, reverse maps
core/matcher.py              ← index BKG O(1) + pipeline matching
core/scoring.py              ← compétitivité + couverture dates
core/excel_exporter.py       ← export Excel formaté
ui/styles.py                 ← CSS global centralisé
ui/components.py             ← composants réutilisables
ui/pagination.py             ← tableau paginé avec filtres
ui/tabs/tab_*.py             ← un fichier par onglet
app.py                       ← point d'entrée (28 lignes)
```

---

### ✨ Nouvelles fonctionnalités

#### Couverture Travel Window brute
- Affichée **dès le chargement** du fichier, avant tout mapping
- Compare les dates de départ ORX aux Check-in BKG sans filtrage
- 5 métriques : dates ORX uniques, dates BKG disponibles, couvertes, manquantes, hors ORX
- Alerte automatique sur les dates ORX absentes du scraping
- Détail dépliable coloré (vert / rouge) date par date
- Complète la couverture enrichie (post-génération) déjà existante

#### Décote Genius BKG
- Nouveau champ `%` dans l'onglet Paramètres (0–50 %, défaut 0 = désactivé)
- Appliqué à **tous** les prix BKG avant calcul de l'écart
- Formule : `Prix BKG Genius = Prix BKG (min) × (1 − décote%)`
- Colonne `Prix BKG Genius` ajoutée dans le rapport si décote > 0
- Bandeau d'information bleu dans le rapport quand la décote est active
- KPI dédié « Décote Genius appliquée » en vert dans les indicateurs généraux

#### Colonne `Politique annulation BKG (brut.)`
- Valeur exacte scraped sur Booking.com, avant normalisation
- Placée côte à côte avec `Politique annulation BKG (norm.)` pour comparaison
- Présente dans le tableau interactif et dans l'export Excel

#### Guide utilisateur permanent
- Affiché via `st.expander()` **avant** le file uploader
- Accessible sans fichier chargé
- Mis à jour pour documenter toutes les nouvelles fonctionnalités

---

### 🐛 Corrections de bugs

#### Préservation de `"NA"` dans Meal Plan BKG
- **Problème :** `pandas.read_excel()` convertissait silencieusement la chaîne `"NA"`
  (logement seul, écrite par le scraper) en `NaN` — la valeur disparaissait du
  multiselect de mapping et ces lignes restaient définitivement N/A.
- **Correction :** `keep_default_na=False` + liste blanche `na_values=_REAL_NA`
  excluant explicitement `"NA"`. Les cellules vides et erreurs Excel (`#N/A`,
  `"NaN"`, `"null"`…) restent correctement parsées comme NaN.

#### Calcul `Prix ORX / chambre` — condition 1*/2* manquante
- **Problème :** le code original multipliait **systématiquement** par 2 le prix ORX,
  sans jamais lire la colonne `Type de prix` — toutes les offres chambres (2*)
  étaient doublées à tort.
- **Correction :** helper `_type_de_prix_str()` qui gère tous les cas pathologiques
  pandas (`None`, `pd.NA`, `float("nan")`, valeurs numériques Excel `1` / `1.0`)
  et conditionne le `× 2` uniquement si la valeur commence par `"1"`.

---

### 🔧 Corrections Pylance / typage statique

| Fichier | Erreur | Correction |
|---|---|---|
| `ui/tabs/__init__.py` | `render_all_tabs` unknown import symbol | Réécriture `with` multi-lignes + `__all__` |
| `ui/__init__.py` | Symboles `ui.components` non résolus | Re-exports explicites + `__all__` |
| `ui/components.py` | Symboles inconnus dans tabs | Ajout `__all__` listant tous les exports publics |
| `core/scoring.py` | `dict[object, int]` ← `dict[Hashable, int]` | Annotation `dict[Any, int]` |
| `core/matcher.py` | Operator `-` not supported `float \| None` | Extraction `_prix_compare() -> tuple[float, float \| None]` |
| `core/data_loader.py` | `reportCallIssue` stubs pandas Overload 4 | `# type: ignore[call-overload]` ciblé + commentaire |

---

### 📚 Documentation

- `README.md` — réécriture complète : structure projet, format Excel, règles de calcul, table des niveaux de compétitivité
- `CHANGELOG.md` — création (ce fichier)
- `ui/tabs/tab_guide.py` — guide étendu de 6 à 9 étapes techniques, table des colonnes du rapport (17 colonnes), légende pilotée par les constantes

---

## [1.0.0] — 2026-05-01

### Version initiale

- Application Streamlit monolithique (`app.py`, ~700 lignes)
- Chargement fichier Excel deux feuilles (ORX + BKG)
- Mapping chambres, pensions, politiques d'annulation
- Calcul écarts ORX vs BKG et scoring compétitivité
- Tableau paginé avec filtres et coloration conditionnelle
- Export rapport Excel avec mise en forme
- Couverture Travel Window enrichie (post-génération)
