"""
tab_rooms.py — Onglet 2 : Mapping catégories ORX → Room Types BKG.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.components import step_title


def render(orx_categories: list[str], bkg_room_types: list[str]) -> dict[str, list[str]]:
    """
    Affiche les multiselects de mapping chambre.
    Retourne room_mapping : {catégorie_orx: [room_types_bkg]}.
    """
    step_title(2, "Mapping — Types de chambres")
    st.caption("Pour chaque catégorie ORX, associez un ou plusieurs types de chambres Booking.")
    st.markdown("")

    room_mapping: dict[str, list[str]] = {}
    for cat in orx_categories:
        room_mapping[cat] = st.multiselect(
            label=f"**{cat}**",
            options=bkg_room_types,
            key=f"room__{cat}",
            placeholder="Types de chambre BKG correspondants...",
        )

    preview = [
        {"Catégorie ORX": c, "Room Type BKG": rt}
        for c, rts in room_mapping.items()
        for rt in rts
    ]
    if preview:
        st.markdown("---")
        st.dataframe(pd.DataFrame(preview), hide_index=True, use_container_width=True)
    else:
        st.warning("⚠️ Aucun mapping chambre défini — toutes les lignes seront N/A.")

    return room_mapping
