# 🏨 Benchmark Tarifaire ORX vs Booking.com

Outil d'analyse de compétitivité tarifaire entre **Orchestra (ORX)** et **Booking.com (BKG)**.  
Développé par **Salah CHERKAOUI** — Équipe Voyage & Loisirs, Showroomprive.

---

## 📋 Fonctionnalités

- **Couverture Travel Window brute** — dès l'upload, avant tout mapping : détecte les trous de scraping
- **Mapping interactif** — chambres, pensions et politiques d'annulation configurables par l'utilisateur
- **Décote Genius** — simulation du prix Booking.com pour les membres Genius (% configurable)
- **Scoring de compétitivité** — 4 niveaux avec seuils personnalisables (Très compétitif / Compétitif / Proche / Non compétitif)
- **Tableau paginé et filtrable** — par date, nb nuits, masquage N/A
- **Export Excel** — feuille `4. RAPPORT DETAILLE` avec coloration conditionnelle et filtres automatiques
- **Guide intégré** — toujours visible avant chargement, avec workflow technique détaillé

---

## 🗂️ Structure du projet

```
travel_hotel_benchmark_report/
│
├── app.py                          # Point d'entrée (< 30 lignes)
├── requirements.txt
│
├── config/
│   └── constants.py                # Seuils, labels, couleurs, largeurs colonnes Excel
│
├── core/                           # Logique métier pure — sans Streamlit
│   ├── data_loader.py              # Lecture Excel + @st.cache_data
│   ├── normalizer.py               # Normalisation prix, pensions, reverse maps
│   ├── matcher.py                  # Index BKG O(1) + pipeline matching ORX↔BKG
│   ├── scoring.py                  # Compétitivité, couverture dates brute/enrichie
│   └── excel_exporter.py           # Génération rapport Excel + @st.cache_data
│
└── ui/                             # Couche présentation — Streamlit uniquement
    ├── styles.py                   # Injection CSS global
    ├── components.py               # Composants réutilisables (kpi, legend, coverage…)
    ├── pagination.py               # Tableau paginé avec filtres
    └── tabs/
        ├── __init__.py             # Orchestration des onglets
        ├── tab_guide.py
        ├── tab_params.py           # Seuils + décote Genius
        ├── tab_rooms.py            # Mapping catégories ORX → Room Types BKG
        ├── tab_pensions.py         # Mapping pensions ORX/BKG → valeurs normalisées
        ├── tab_cancel.py           # Mapping politiques d'annulation BKG
        └── tab_report.py           # Génération rapport + export Excel
```

---

## 📥 Format du fichier Excel attendu

Le fichier `.xlsx` doit contenir **deux feuilles** :

| Feuille | Contenu |
|---|---|
| `1. INPUT ORX EXPORT` | Export Orchestra avec colonnes : `Date de départ`, `Nb nuits`, `Catégorie`, `Pension`, `Type de prix`, `Prix de vente TTC` |
| `2. OUTPUT BKG SCRAP` | Scraping Booking.com avec colonnes : `Check-in`, `Room Type`, `Meal Plan`, `Cancellation Policy`, `Price` |

> **Note :** la valeur `"NA"` dans la colonne `Meal Plan` est conservée comme chaîne (logement seul) et ne sera pas interprétée comme NaN.

---

## ⚙️ Prérequis

- Python 3.10+
- pip

---

## 🚀 Installation & Lancement

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd travel_hotel_benchmark_report

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run app.py
```

---

## ☁️ Déploiement sur Streamlit Community Cloud

1. Poussez le code sur un dépôt GitHub.
2. Rendez-vous sur [share.streamlit.io](https://share.streamlit.io/).
3. Connectez-vous avec votre compte GitHub.
4. Sélectionnez le dépôt — `app.py` sera détecté automatiquement.
5. Cliquez sur **Deploy**.

---

## 🔧 Dépendances

```
streamlit>=1.35.0
pandas>=2.2.0
openpyxl>=3.1.2
```

---

## 📐 Logique de calcul

### Prix de comparaison

| Type de prix ORX | Calcul |
|---|---|
| `1*` (par personne) | `Prix TTC × 2` |
| `2*` (par chambre) | `Prix TTC × 1` |

### Décote Genius (optionnelle)

```
Prix BKG Genius = Prix BKG (min) × (1 − décote%)
Ecart EUR       = Prix ORX / chambre − Prix BKG Genius
Ecart %         = Ecart EUR / Prix BKG Genius
```

### Niveaux de compétitivité (seuils par défaut)

| Niveau | Condition |
|---|---|
| ✅ Très compétitif | Ecart ≤ −20 % |
| ✅ Compétitif | −20 % < Ecart ≤ −15 % |
| ⚠️ Proche | −15 % < Ecart ≤ −10 % |
| ❌ Non compétitif | Ecart > −10 % |