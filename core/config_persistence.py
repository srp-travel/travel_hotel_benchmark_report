"""
config_persistence.py — Sauvegarde et restauration du mapping utilisateur.

Format JSON exporté :
{
  "version": "2.0",
  "saved_at": "2026-06-02T12:00:00",
  "room_mapping":   { "Chambre double": ["Chambre Double", ...] },
  "pension_config": { "DP - Demi-pension": {"orx": [...], "bkg": [...]} },
  "cancel_config":  { "AG - Annulation gratuite": {"bkg": [...]} },
  "params": {
    "seuil_non_competitif": -0.10,
    "seuil_competitif": -0.15,
    "seuil_tres_competitif": -0.20,
    "genius_decote": 0.0,
    "ref_policy": "RF - Remboursable"
  }
}

Correspondance clés session_state ↔ widgets Streamlit :
  room__<cat>          → st.multiselect  tab_rooms
  p_orx__<norm>        → st.multiselect  tab_pensions (côté ORX)
  p_bkg__<norm>        → st.multiselect  tab_pensions (côté BKG)
  c_bkg__<norm>        → st.multiselect  tab_cancel
  seuil_proche_input   → st.number_input tab_params
  seuil_comp_input     → st.number_input tab_params
  seuil_tres_input     → st.number_input tab_params
  genius_input         → st.number_input tab_params
  ref_policy_input     → st.selectbox    tab_params
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import streamlit as st

CONFIG_VERSION = "2.0"


def build_config_dict(
    room_mapping:   dict[str, list[str]],
    pension_config: dict[str, dict[str, list[str]]],
    cancel_config:  dict[str, dict[str, list[str]]],
    params:         dict[str, float],
    ref_policy:     str,
) -> dict[str, Any]:
    """Sérialise la configuration courante en dict JSON-compatible."""
    return {
        "version":        CONFIG_VERSION,
        "saved_at":       datetime.now().isoformat(timespec="seconds"),
        "room_mapping":   room_mapping,
        "pension_config": pension_config,
        "cancel_config":  cancel_config,
        "params": {
            "seuil_non_competitif":  params.get("seuil_non_competitif",  -0.10),
            "seuil_competitif":      params.get("seuil_competitif",      -0.15),
            "seuil_tres_competitif": params.get("seuil_tres_competitif", -0.20),
            "genius_decote":         params.get("genius_decote",          0.0),
            "ref_policy":            ref_policy,
        },
    }


def config_to_json(config: dict[str, Any]) -> str:
    """Sérialise en JSON indenté (pour le bouton de téléchargement)."""
    return json.dumps(config, ensure_ascii=False, indent=2)


def load_config_from_bytes(raw: bytes) -> dict[str, Any]:
    """Parse le JSON uploadé. Lève ValueError si le format est invalide."""
    try:
        data: dict[str, Any] = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Fichier JSON invalide : {e}") from e

    if "room_mapping" not in data:
        raise ValueError("Clé 'room_mapping' absente — fichier de config incorrect.")
    return data


def apply_config_to_session(config: dict[str, Any]) -> None:
    """
    Injecte toutes les valeurs du JSON dans st.session_state
    avec les clés exactes attendues par les widgets Streamlit.
    Un st.rerun() doit suivre cet appel pour rafraîchir les widgets.
    """
    # ── Mapping chambres ──────────────────────────────────────
    for cat, rooms in config.get("room_mapping", {}).items():
        st.session_state[f"room__{cat}"] = rooms

    # ── Mapping pensions ──────────────────────────────────────
    for norm, vals in config.get("pension_config", {}).items():
        st.session_state[f"p_orx__{norm}"] = vals.get("orx", [])
        st.session_state[f"p_bkg__{norm}"] = vals.get("bkg", [])

    # ── Mapping annulations ───────────────────────────────────
    for norm, vals in config.get("cancel_config", {}).items():
        st.session_state[f"c_bkg__{norm}"] = vals.get("bkg", [])

    # ── Paramètres ────────────────────────────────────────────
    p = config.get("params", {})

    # number_inputs : session_state stocke la valeur entière affichée (ex. -10)
    if "seuil_non_competitif" in p:
        st.session_state["seuil_proche_input"] = int(p["seuil_non_competitif"]  * 100)
    if "seuil_competitif" in p:
        st.session_state["seuil_comp_input"]   = int(p["seuil_competitif"]      * 100)
    if "seuil_tres_competitif" in p:
        st.session_state["seuil_tres_input"]   = int(p["seuil_tres_competitif"] * 100)
    if "genius_decote" in p:
        st.session_state["genius_input"]       = int(p["genius_decote"]         * 100)

    # selectbox : session_state stocke la valeur sélectionnée (string)
    if "ref_policy" in p:
        st.session_state["ref_policy_input"] = p["ref_policy"]
