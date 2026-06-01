"""
tab_guide.py — Onglet Guide : documentation utilisateur et workflow technique.
Mis à jour pour refléter toutes les fonctionnalités de la version restructurée.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config.constants import (
    DEFAULT_GENIUS_DECOTE,
    DEFAULT_SEUIL_PROCHE,
    DEFAULT_SEUIL_COMPETITIF,
    DEFAULT_SEUIL_TRES_COMPETITIF,
)


def render() -> None:

    # ── Bannière d'accueil ─────────────────────────────────────
    st.markdown("""
<div style="background:#EEF4FF;border-left:5px solid #1F3864;border-radius:8px;
            padding:20px 24px;margin-bottom:28px;">
    <div style="font-size:22px;font-weight:800;color:#1F3864;margin-bottom:6px;">
        🏨 Bienvenue sur le Benchmark Tarifaire
    </div>
    <div style="font-size:15px;color:#444;">
        Comparez en quelques clics les prix de vente Orchestra avec les prix
        Booking.com scraped — et identifiez instantanément où vous êtes compétitif.
    </div>
</div>
""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # PARTIE 1 — GUIDE UTILISATEUR
    # ══════════════════════════════════════════════════════════
    st.markdown("## 🧭 Partie 1 — Guide d'utilisation")
    st.caption("Les 6 étapes pour obtenir votre rapport de compétitivité.")
    st.markdown("")

    _card = (
        '<div style="background:#fff;border:1px solid #E0E0E0;border-radius:10px;'
        'padding:18px 20px;margin-bottom:14px;">'
        '<div style="font-size:16px;font-weight:700;color:#1F3864;margin-bottom:8px;">'
        '{icon} {title}</div>'
        '<div style="font-size:14px;color:#444;line-height:1.7;">{body}</div>'
        '</div>'
    )

    g1, g2 = st.columns(2, gap="large")

    with g1:
        st.markdown(_card.format(
            icon="📂", title="Étape 1 — Chargez votre fichier",
            body=(
                "Glissez votre fichier <b>.xlsx</b> dans la zone de chargement.<br>"
                "Il doit contenir <b>deux feuilles</b> :<br>"
                "<ul style='margin:6px 0 0 16px;'>"
                "<li><b>1. INPUT ORX EXPORT</b> — export Orchestra</li>"
                "<li><b>2. OUTPUT BKG SCRAP</b> — scraping Booking.com</li>"
                "</ul>"
                "Dès le chargement, un bloc <b>Couverture Travel Window brute</b> "
                "s'affiche automatiquement : il compare les dates ORX aux Check-in BKG "
                "<i>avant tout mapping</i> pour détecter les trous de scraping."
            ),
        ), unsafe_allow_html=True)

        st.markdown(_card.format(
            icon="⚙️", title="Étape 2 — Configurez les paramètres",
            body=(
                "<b>Seuils de compétitivité</b> — valeurs négatives en % "
                f"(défauts : {DEFAULT_SEUIL_PROCHE} / {DEFAULT_SEUIL_COMPETITIF} / "
                f"{DEFAULT_SEUIL_TRES_COMPETITIF} %).<br><br>"
                "<b>Décote Genius</b> — pourcentage appliqué à tous les prix BKG "
                "avant calcul de l'écart (défaut : "
                f"{DEFAULT_GENIUS_DECOTE} % = désactivée). Simule le tarif affiché "
                "aux membres Genius Booking.com.<br>"
                "Exemple : prix BKG 100 € avec décote 10 % → comparaison sur 90 €."
            ),
        ), unsafe_allow_html=True)

        st.markdown(_card.format(
            icon="🛏️", title="Étape 3 — Mappez les chambres",
            body=(
                "Pour chaque <b>catégorie ORX</b>, sélectionnez les "
                "<b>types de chambre Booking</b> équivalents.<br>"
                "Sans ce mapping, toutes les lignes de la catégorie seront <b>N/A</b>."
            ),
        ), unsafe_allow_html=True)

    with g2:
        st.markdown(_card.format(
            icon="🍽️", title="Étape 4 — Mappez les pensions",
            body=(
                "Associez les libellés ORX et BKG à une valeur normalisée commune "
                "(ex. <i>PDJ, DP, PC, TI, LS</i>).<br>"
                "La comparaison n'est effectuée <b>qu'entre pensions de même type</b>.<br><br>"
                "<b>Note :</b> la valeur <code>NA</code> dans le scraping BKG "
                "(absence d'info pension) est préservée telle quelle et peut être "
                "mappée sur <i>LS — Logement seul</i>."
            ),
        ), unsafe_allow_html=True)

        st.markdown(_card.format(
            icon="📋", title="Étape 5 — Mappez les annulations",
            body=(
                "Normalisez les politiques d'annulation BKG "
                "(ex. <i>Free cancellation → AG</i>).<br>"
                "Le rapport affiche deux colonnes côte à côte :<br>"
                "<ul style='margin:6px 0 0 16px;'>"
                "<li><b>Politique annulation BKG (brut.)</b> — valeur exacte scraped</li>"
                "<li><b>Politique annulation BKG (norm.)</b> — valeur normalisée via votre mapping</li>"
                "</ul>"
            ),
        ), unsafe_allow_html=True)

        st.markdown(_card.format(
            icon="📊", title="Étape 6 — Générez le rapport",
            body=(
                "Cliquez sur <b>Générer le rapport</b> dans l'onglet Rapport.<br>"
                "Vous obtenez :<br>"
                "<ul style='margin:6px 0 0 16px;'>"
                "<li>KPIs synthétiques (écarts moyens, taux couverture enrichie…)</li>"
                "<li>Tableau coloré paginé et filtrable</li>"
                "<li>Couverture Travel Window <b>enrichie</b> (après mapping complet)</li>"
                "<li>Export Excel avec feuille <code>4. RAPPORT DETAILLE</code></li>"
                "</ul>"
            ),
        ), unsafe_allow_html=True)

    st.markdown("""
<div style="background:#F0FFF4;border:1px solid #B7EBD0;border-radius:10px;
            padding:14px 20px;margin-top:4px;">
    <div style="font-size:14px;color:#375623;">
        💡 <b>Astuce</b> — Le rapport est <b>persistant</b> : naviguez librement
        entre les onglets sans perdre vos résultats. Cliquez sur <i>Générer</i>
        à nouveau uniquement si vous modifiez un mapping ou un seuil.
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Légende des couleurs ───────────────────────────────────
    st.markdown("")
    st.markdown("#### 🎨 Lecture des couleurs")
    leg_data = [
        ("#C6EFCE", "✅ Très compétitif",
         f"Ecart ≤ {DEFAULT_SEUIL_TRES_COMPETITIF}%",
         "Prix ORX nettement inférieur à Booking"),
        ("#E2EFDA", "✅ Compétitif",
         f"{DEFAULT_SEUIL_TRES_COMPETITIF}% < Ecart ≤ {DEFAULT_SEUIL_COMPETITIF}%",
         "Bonne position tarifaire"),
        ("#FFEB9C", "⚠️ Proche",
         f"{DEFAULT_SEUIL_COMPETITIF}% < Ecart ≤ {DEFAULT_SEUIL_PROCHE}%",
         "Vigilance — surveiller l'évolution"),
        ("#FFC7CE", "❌ Non compétitif",
         f"Ecart > {DEFAULT_SEUIL_PROCHE}%",
         "Prix ORX supérieur ou trop proche de Booking"),
        ("#F2F2F2", "⬜ N/A",
         "—",
         "Aucune correspondance BKG trouvée pour cette ligne"),
    ]
    st.dataframe(
        pd.DataFrame(leg_data, columns=["Couleur", "Indicateur", "Condition", "Interprétation"])
        .style.apply(
            lambda row: [f"background-color:{row['Couleur']};font-weight:600"] * 4,
            axis=1,
        ),
        hide_index=True,
        use_container_width=True,
    )

    # ── Colonnes du rapport ────────────────────────────────────
    st.markdown("")
    st.markdown("#### 📄 Colonnes du rapport détaillé")
    col_data = [
        ("Date de départ",                     "ORX",  "Date de check-in"),
        ("Nb nuits",                           "ORX",  "Durée du séjour"),
        ("Catégorie ORX",                      "ORX",  "Catégorie de chambre Orchestra"),
        ("Pension ORX (norm.)",                "ORX",  "Pension normalisée (PDJ, DP, PC, TI, LS)"),
        ("Politique annulation ORX (réf.)",    "ORX",  "Politique de référence choisie dans Paramètres"),
        ("Type de prix",                       "ORX",  "1* = par personne, 2* = par chambre"),
        ("Prix de vente TTC",                  "ORX",  "Prix brut de la feuille ORX"),
        ("Prix ORX / chambre",                 "ORX",  "Prix converti en base chambre 2 personnes"),
        ("Room Type BKG",                      "BKG",  "Type de chambre Booking retenu (prix minimum)"),
        ("Meal Plan BKG",                      "BKG",  "Libellé brut du meal plan Booking"),
        ("Meal Plan BKG (norm.)",              "BKG",  "Meal plan normalisé via mapping"),
        ("Politique annulation BKG (brut.)",   "BKG",  "Valeur exacte scraped sur Booking"),
        ("Politique annulation BKG (norm.)",   "BKG",  "Politique normalisée via mapping"),
        ("Prix BKG (min)",                     "BKG",  "Prix minimum scraped toutes chambres mappées"),
        ("Prix BKG Genius",                    "BKG",  "Prix BKG × (1 − décote Genius) — visible si décote > 0"),
        ("Ecart EUR",                          "Calc", "Prix ORX/chambre − Prix BKG comparé"),
        ("Ecart PCT",                          "Calc", "(Prix ORX − Prix BKG comparé) / Prix BKG comparé"),
    ]
    st.dataframe(
        pd.DataFrame(col_data, columns=["Colonne", "Source", "Description"]),
        hide_index=True,
        use_container_width=True,
    )

    # ══════════════════════════════════════════════════════════
    # PARTIE 2 — WORKFLOW TECHNIQUE
    # ══════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("## ⚙️ Partie 2 — Workflow des traitements")
    st.caption("Description du pipeline de normalisation et de comparaison.")
    st.markdown("")

    _workflow_items = [
        (
            "① Chargement & nettoyage des données",
            "Les deux feuilles sont lues avec <code>keep_default_na=False</code> "
            "et une liste blanche de valeurs NA explicite.<br>"
            "Cela préserve la chaîne <code>\"NA\"</code> (logement seul scraped) "
            "qui serait sinon silencieusement convertie en NaN par pandas.<br>"
            "Les en-têtes sont normalisés (<code>str.strip()</code>) "
            "et les dates parsées en objets <code>date</code> Python.",
        ),
        (
            "② Couverture Travel Window brute (avant mapping)",
            "Dès le chargement, <code>compute_raw_date_coverage()</code> compare "
            "les dates de départ ORX aux Check-in BKG sans aucun filtre.<br>"
            "Métriques affichées : dates ORX uniques, dates BKG disponibles, "
            "dates couvertes, dates manquantes, dates BKG hors ORX.<br>"
            "Permet de détecter les trous de scraping <b>avant</b> de configurer les mappings.",
        ),
        (
            "③ Normalisation des pensions",
            "Chaque libellé brut ORX et BKG est converti en valeur canonique "
            "(<code>PDJ, DP, PC, TI, LS</code>) via les reverse maps construites "
            "depuis la configuration utilisateur.<br>"
            "La pré-normalisation BKG est effectuée <b>une seule fois</b> "
            "dans <code>build_bkg_index()</code>.",
        ),
        (
            "④ Normalisation du prix ORX → prix chambre",
            "Les prix BKG sont toujours <b>par chambre pour 2 personnes</b>.<br>"
            "<ul style='margin:8px 0 0 18px;'>"
            "<li>Type <b>1*</b> (par personne) → <code>× 2</code></li>"
            "<li>Type <b>2*</b> (par chambre) → utilisé tel quel</li>"
            "</ul>"
            "Le helper <code>_type_de_prix_str()</code> gère tous les cas pathologiques "
            "pandas : <code>None</code>, <code>pd.NA</code>, <code>float('nan')</code>, "
            "valeurs numériques Excel (int 1 → \"1\").",
        ),
        (
            "⑤ Index BKG O(1) + Matching ORX↔BKG",
            "Un dict pré-indexé <code>(date, meal_norm, room_type) → ligne min</code> "
            "est construit avant la boucle (O(n log n) une fois, O(1) par lookup).<br>"
            "Filtre séquentiel : <b>date exacte</b> → <b>type de chambre mappé</b> → "
            "<b>même pension normalisée</b>.<br>"
            "Plusieurs correspondances → <b>prix minimum</b> retenu.",
        ),
        (
            "⑥ Décote Genius (optionnelle)",
            "Si <code>genius_decote > 0</code>, le prix de comparaison devient "
            "<code>Prix BKG × (1 − décote)</code>.<br>"
            "<code>Prix BKG (min)</code> reste le tarif scraped original.<br>"
            "<code>Prix BKG Genius</code> est ajouté comme colonne supplémentaire.<br>"
            "L'écart EUR et l'écart % sont calculés sur le prix ajusté.",
        ),
        (
            "⑦ Calcul des écarts & scoring",
            "<div style='background:#fff;border:1px solid #e0e0e0;border-radius:6px;"
            "padding:12px 16px;font-family:monospace;font-size:14px;'>"
            "Ecart EUR = Prix ORX/chambre − Prix BKG comparé<br>"
            "Ecart %   = (Prix ORX − Prix BKG comparé) / Prix BKG comparé</div><br>"
            "L'Ecart % est comparé aux seuils configurés pour attribuer "
            "l'un des 4 niveaux de compétitivité.",
        ),
        (
            "⑧ Couverture Travel Window enrichie (après génération)",
            "Après matching complet, <code>compute_date_coverage()</code> analyse "
            "la couverture par combinaison <b>(Date de départ × Nb nuits)</b> "
            "en tenant compte du mapping chambre + pension.<br>"
            "Ce taux est plus exigeant que la couverture brute : "
            "une date peut être présente dans BKG mais absente après mapping.",
        ),
        (
            "⑨ Production du rapport",
            "<ul style='margin:8px 0 0 18px;line-height:2.0;'>"
            "<li><b>KPIs</b> — écarts moyens/min/max, répartition par niveau, "
            "taux couverture, décote Genius appliquée</li>"
            "<li><b>Tableau interactif</b> — filtres date/nuits/N/A, pagination</li>"
            "<li><b>Export Excel</b> — feuille <code>4. RAPPORT DETAILLE</code> "
            "avec coloration conditionnelle, freeze pane, filtres auto</li>"
            "</ul>",
        ),
    ]

    for title, body in _workflow_items:
        st.markdown(
            f'<div style="background:#F8F9FA;border:1px solid #DEE2E6;'
            f'border-radius:10px;padding:20px 24px;margin-bottom:16px;">'
            f'<div style="font-size:16px;font-weight:700;color:#1F3864;'
            f'margin-bottom:12px;">{title}</div>'
            f'<div style="font-size:14px;color:#444;line-height:1.8;">{body}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )