"""Accessible and multilingual election material checks."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ElectionAccessibilityReview:
    material_name: str
    checks: tuple[str, ...]
    civicaccess_handoff_recommended: bool


def review_accessible_material(material_name: str, languages: list[str]) -> ElectionAccessibilityReview:
    normalized = tuple(lang.strip() for lang in languages if lang.strip()) or ("English",)
    return ElectionAccessibilityReview(material_name.strip(), ("Plain-language review", "Accessible format review", *(f"Language variant: {lang}" for lang in normalized)), True)
