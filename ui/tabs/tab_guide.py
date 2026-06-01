"""
tab_guide.py — Onglet Guide : documentation utilisateur et workflow technique.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config.constants import DEFAULT_SEUIL_PROCHE, DEFAULT_SEUIL_COMPETITIF, DEFAULT_SEUIL_TRES_COMPETITIF


def render() -> None:
    st.markdown("""
<div style="background:#EEF4FF;border-left:5px solid #1F3864;border-radius:8px;padding:20px 24px;margin-bottom:28px;">
    <div style="font-size:22px;font-weight:800;color:#1F3864;margin-bottom:6px;">🏨 Bienvenue sur le Benchmark Tarifaire</div>
    <div style="font-size:15px;color:#444;">
        Cet outil vous permet de comparer en quelques clics les prix de vente Orchestra
        avec les prix en temps réel scraped sur Booking.com — et d'identifier en un coup d'œil
        où vous êtes compétitif, et où vous ne l'êtes pas.
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("## 🧭 Partie 1 — Comment ça marche ?")
    st.caption("Guide simple et rapide pour prendre l'outil en main.")
    st.markdown("")

    g1, g2 = st.columns(2, gap="large")

    _card_html = """
<div style="background:#fff;border:1px solid #E0E0E0;border-radius:10px;padding:18px 20px;margin-bottom:16px;">
    <div style="font-size:16px;font-weight:700;color:#1F3864;margin-bottom:8px;">{icon} {title}</div>
    <div style="font-size:14px;color:#444;line-height:1.7;">{body}</div>
</div>
"""

    with g1:
        st.markdown(_card_html.format(
            icon="📂", title="Étape 1 — Chargez votre fichier",
            body="Glissez votre fichier <b>.xlsx</b> dans la zone de chargement.<br>"
                 "Il doit contenir <b>deux feuilles</b> :<br>"
                 "<ul style='margin:6px 0 0 16px;'>"
                 "<li><b>1. INPUT ORX EXPORT</b> — votre export Orchestra</li>"
                 "<li><b>2. OUTPUT BKG SCRAP</b> — le scraping Booking.com</li></ul>"
                 "L'outil détecte automatiquement les catégories, pensions et types de chambres disponibles.",
        ), unsafe_allow_html=True)

        st.markdown(_card_html.format(
            icon="⚙️", title="Étape 2 — Configurez les seuils",
            body=f"Dans l'onglet <b>Paramètres</b>, définissez vos seuils de compétitivité en %.<br>"
                 f"Les valeurs par défaut sont "
                 f"<b>{DEFAULT_SEUIL_PROCHE} / {DEFAULT_SEUIL_COMPETITIF} / {DEFAULT_SEUIL_TRES_COMPETITIF} %</b> "
                 "mais vous pouvez les ajuster selon votre stratégie tarifaire.",
        ), unsafe_allow_html=True)

        st.markdown(_card_html.format(
            icon="🛏️", title="Étape 3 — Mappez les chambres",
            body="Pour chaque <b>catégorie ORX</b>, sélectionnez les <b>types de chambre Booking</b> équivalents.<br>"
                 "Sans ce mapping, aucune comparaison ne sera possible.",
        ), unsafe_allow_html=True)

    with g2:
        st.markdown(_card_html.format(
            icon="🍽️", title="Étape 4 — Mappez les pensions",
            body="Associez les libellés ORX et BKG à une valeur normalisée commune (ex. <i>PDJ, DP, PC, TI, LS</i>).<br>"
                 "La comparaison n'est effectuée <b>qu'entre pensions de même type</b>.",
        ), unsafe_allow_html=True)

        st.markdown(_card_html.format(
            icon="📋", title="Étape 5 — Mappez les annulations",
            body="Normalisez les politiques d'annulation BKG (ex. <i>Free cancellation → AG</i>).<br>"
                 "La politique ORX de référence sert uniquement à l'affichage dans le rapport.",
        ), unsafe_allow_html=True)

        st.markdown(_card_html.format(
            icon="📊", title="Étape 6 — Générez le rapport",
            body="Cliquez sur <b>Générer le rapport</b> dans l'onglet Rapport.<br>"
                 "Vous obtenez instantanément :<br>"
                 "<ul style='margin:6px 0 0 16px;'>"
                 "<li>Un tableau coloré selon la compétitivité</li>"
                 "<li>Des KPIs synthétiques (écarts moyens, taux de couverture…)</li>"
                 "<li>Un fichier Excel exportable avec mise en forme automatique</li></ul>",
        ), unsafe_allow_html=True)

    st.markdown("""
<div style="background:#F0FFF4;border:1px solid #B7EBD0;border-radius:10px;padding:14px 20px;margin-top:4px;">
    <div style="font-size:14px;color:#375623;">
        💡 <b>Astuce</b> — Le rapport est <b>persistant</b> : naviguez entre les onglets sans perdre vos résultats.
        Recliquez sur <i>Générer</i> uniquement si vous modifiez un mapping ou un seuil.
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("#### 🎨 Lecture des couleurs")
    leg_data = [
        ("#C6EFCE", "✅ Très compétitif",  f"Ecart ≤ {DEFAULT_SEUIL_TRES_COMPETITIF}%",           "Prix nettement inférieur à Booking"),
        ("#E2EFDA", "✅ Compétitif",        f"{DEFAULT_SEUIL_TRES_COMPETITIF}% < Ecart ≤ {DEFAULT_SEUIL_COMPETITIF}%",  "Bonne position tarifaire"),
        ("#FFEB9C", "⚠️ Proche",            f"{DEFAULT_SEUIL_COMPETITIF}% < Ecart ≤ {DEFAULT_SEUIL_PROCHE}%",  "Vigilance — surveiller l'évolution"),
        ("#FFC7CE", "❌ Non compétitif",    f"Ecart > {DEFAULT_SEUIL_PROCHE}%",                    "Prix ORX supérieur ou trop proche de Booking"),
        ("#F2F2F2", "⬜ N/A",               "—",                                                   "Aucune correspondance BKG trouvée"),
    ]
    st.dataframe(
        pd.DataFrame(leg_data, columns=["Couleur", "Indicateur", "Condition", "Interprétation"])
        .style.apply(
            lambda row: [f"background-color:{row['Couleur']};font-weight:600"] * 4,  # type: ignore[return-value]
            axis=1,
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("## ⚙️ Partie 2 — Workflow des traitements")
    st.caption("Description technique du pipeline de normalisation et de comparaison.")
    st.markdown("")

    _workflow_items = [
        ("① Chargement & nettoyage des données",
         "<b>Feuille ORX</b> — chaque ligne représente une offre Orchestra avec son prix TTC, sa catégorie, "
         "sa pension, son type de prix (1* = par personne, 2* = par chambre) et sa date de départ.<br>"
         "<b>Feuille BKG</b> — chaque ligne est un prix scraping Booking avec la date de check-in, "
         "le type de chambre, le meal plan, la politique d'annulation et le prix total pour 2 personnes.<br><br>"
         "Les en-têtes sont normalisés (<code>str.strip()</code>) et les dates parsées en objets <code>date</code> Python."),

        ("② Normalisation des pensions",
         "Chaque libellé brut ORX (ex. <i>\"Petit déjeuner inclus\"</i>) et BKG (ex. <i>\"Breakfast included\"</i>) "
         "est converti en valeur canonique : <code>PDJ</code>, <code>DP</code>, <code>PC</code>, <code>TI</code>, <code>LS</code>.<br><br>"
         "La pré-normalisation BKG est effectuée <b>une seule fois avant la boucle</b> (via <code>build_bkg_index()</code>). "
         "Les libellés non mappés sont flaggés <i>\"Non mappé : …\"</i>."),

        ("③ Normalisation du prix ORX → prix chambre",
         "Les prix BKG sont toujours <b>par chambre pour 2 personnes</b>.<br>"
         "<ul style='margin:8px 0 0 18px;'>"
         "<li><b>1*</b> (prix par personne) → × 2 pour obtenir le prix chambre</li>"
         "<li><b>2*</b> (prix par chambre) → utilisé tel quel</li></ul>"),

        ("④ Matching ORX ↔ BKG",
         "Filtre séquentiel strict via un <b>index dict O(1)</b> pré-calculé avant la boucle :<br>"
         "<ol style='margin:8px 0 0 18px;line-height:2.0;'>"
         "<li><b>Date exacte</b> — <code>Date de départ ORX == Check-in BKG</code></li>"
         "<li><b>Type de chambre mappé</b> — Room Type BKG dans la liste associée à la catégorie ORX</li>"
         "<li><b>Même pension normalisée</b> — <code>_meal_norm BKG == pension_norm ORX</code></li></ol>"
         "Lorsque plusieurs BKG correspondent, le <b>prix minimum</b> est retenu."),

        ("⑤ Calcul des écarts & scoring",
         "<div style='background:#fff;border:1px solid #e0e0e0;border-radius:6px;padding:12px 16px;"
         "font-family:monospace;font-size:14px;'>"
         "Ecart EUR = Prix ORX/chambre − Prix BKG<br>"
         "Ecart %   = (Prix ORX/chambre − Prix BKG) / Prix BKG</div><br>"
         "L'Ecart % est comparé aux seuils pour attribuer l'un des 4 niveaux de compétitivité."),

        ("⑥ Production du rapport",
         "<ul style='margin:8px 0 0 18px;line-height:2.0;'>"
         "<li><b>KPIs synthétiques</b> — écarts moyens/min/max, répartition par niveau, taux de couverture</li>"
         "<li><b>Tableau interactif</b> — filtrable par date, par nb nuits, masquage N/A, paginé</li>"
         "<li><b>Export Excel</b> — feuille <code>4. RAPPORT DETAILLE</code> avec coloration conditionnelle et filtres auto</li></ul>"),
    ]

    for title, body in _workflow_items:
        st.markdown(
            f'<div style="background:#F8F9FA;border:1px solid #DEE2E6;border-radius:10px;'
            f'padding:20px 24px;margin-bottom:20px;">'
            f'<div style="font-size:16px;font-weight:700;color:#1F3864;margin-bottom:12px;">{title}</div>'
            f'<div style="font-size:14px;color:#444;line-height:1.8;">{body}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
