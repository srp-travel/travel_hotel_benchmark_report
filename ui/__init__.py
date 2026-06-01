"""
ui/__init__.py — Re-exports explicites des composants publics.
Permet à Pylance de résoudre `from ui.components import step_title` etc.
sans ambiguïté, même en présence d'un cache périmé.
"""

from ui.components import (
    kpi,
    render_coverage_block,
    render_footer,
    render_legend,
    render_raw_coverage_block,
    render_seuil_stats,
    step_title,
)

__all__ = [
    "kpi",
    "render_coverage_block",
    "render_footer",
    "render_legend",
    "render_raw_coverage_block",
    "render_seuil_stats",
    "step_title",
]