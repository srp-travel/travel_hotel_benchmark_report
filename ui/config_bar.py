"""
config_bar.py — Barre de sauvegarde/restauration du mapping utilisateur.
"""

from __future__ import annotations

import streamlit as st

from core.config_persistence import (
    apply_config_to_session,
    build_config_dict,
    config_to_json,
    load_config_from_bytes,
)

__all__ = ["render_config_bar"]

_MAPPING_PREFIXES = ("room__", "p_orx__", "p_bkg__", "c_bkg__")
_PARAM_KEYS = (
    "seuil_proche_input", "seuil_comp_input", "seuil_tres_input",
    "genius_input", "ref_policy_input",
)


def _collect_current_config() -> dict:
    """Reconstruit la config depuis st.session_state (état courant des widgets)."""
    room_mapping:   dict[str, list[str]]             = {}
    pension_config: dict[str, dict[str, list[str]]]  = {}
    cancel_config:  dict[str, dict[str, list[str]]]  = {}

    for raw_key, val in st.session_state.items():
        # st.session_state peut avoir des clés int (widgets internes Streamlit)
        # → on filtre pour ne traiter que les clés str
        if not isinstance(raw_key, str):
            continue
        key: str = raw_key

        if key.startswith("room__"):
            cat = key[len("room__"):]
            room_mapping[cat] = list(val) if val else []

        elif key.startswith("p_orx__"):
            norm = key[len("p_orx__"):]
            pension_config.setdefault(norm, {"orx": [], "bkg": []})
            pension_config[norm]["orx"] = list(val) if val else []

        elif key.startswith("p_bkg__"):
            norm = key[len("p_bkg__"):]
            pension_config.setdefault(norm, {"orx": [], "bkg": []})
            pension_config[norm]["bkg"] = list(val) if val else []

        elif key.startswith("c_bkg__"):
            norm = key[len("c_bkg__"):]
            cancel_config[norm] = {"bkg": list(val) if val else []}

    params = {
        "seuil_non_competitif":  int(st.session_state.get("seuil_proche_input", -10)) / 100,
        "seuil_competitif":      int(st.session_state.get("seuil_comp_input",   -15)) / 100,
        "seuil_tres_competitif": int(st.session_state.get("seuil_tres_input",   -20)) / 100,
        "genius_decote":         int(st.session_state.get("genius_input",          0)) / 100,
    }
    ref_policy: str = str(st.session_state.get("ref_policy_input", "RF - Remboursable"))

    return build_config_dict(room_mapping, pension_config, cancel_config, params, ref_policy)


def _reset_mapping_keys() -> None:
    """Supprime toutes les clés de mapping de session_state."""
    to_delete = [
        k for k in list(st.session_state.keys())
        if isinstance(k, str) and (
            any(k.startswith(p) for p in _MAPPING_PREFIXES) or k in _PARAM_KEYS
        )
    ]
    for k in to_delete:
        del st.session_state[k]


def render_config_bar() -> None:
    """
    Affiche la barre de configuration persistante.
    Doit être appelée AVANT le rendu des onglets de mapping.
    """
    with st.container(border=True):
        st.markdown(
            '<div style="font-size:13px;font-weight:700;text-transform:uppercase;'
            'letter-spacing:.06em;color:#1F3864;margin-bottom:10px;">'
            '💾 Configuration du mapping</div>',
            unsafe_allow_html=True,
        )

        col_load, col_save, col_reset, col_info = st.columns([2, 2, 1, 3])

        # ── Charger une config ─────────────────────────────────
        with col_load:
            uploaded_cfg = st.file_uploader(
                "Charger une config",
                type=["json"],
                key="config_uploader",
                label_visibility="collapsed",
                help="Charger un fichier .json exporté précédemment",
            )
            if uploaded_cfg is not None:
                file_id = f"{uploaded_cfg.name}_{uploaded_cfg.size}"
                if st.session_state.get("_last_config_loaded") != file_id:
                    try:
                        config = load_config_from_bytes(uploaded_cfg.read())
                        apply_config_to_session(config)
                        st.session_state["_last_config_loaded"] = file_id
                        st.session_state["_config_load_msg"] = (
                            f"✅ Config chargée — sauvegardée le {config.get('saved_at', '?')}"
                        )
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        # ── Sauvegarder la config ──────────────────────────────
        with col_save:
            current_config = _collect_current_config()
            st.download_button(
                label="⬇️ Sauvegarder la config",
                data=config_to_json(current_config),
                file_name="benchmark_mapping_config.json",
                mime="application/json",
                use_container_width=True,
                help="Télécharge la configuration courante au format JSON",
            )

        # ── Réinitialiser ──────────────────────────────────────
        with col_reset:
            if st.button("🗑️", help="Réinitialiser tous les mappings",
                         use_container_width=True):
                _reset_mapping_keys()
                st.session_state["_last_config_loaded"] = None
                st.session_state.pop("_config_load_msg", None)
                st.rerun()

        # ── Message de statut ──────────────────────────────────
        with col_info:
            if msg := st.session_state.get("_config_load_msg"):
                st.success(msg)
            else:
                has_mapping = any(
                    isinstance(k, str) and any(k.startswith(p) for p in _MAPPING_PREFIXES)
                    for k in st.session_state
                )
                if has_mapping:
                    st.info("📋 Mapping en cours — pensez à sauvegarder.")
                else:
                    st.caption("Aucune configuration chargée.")