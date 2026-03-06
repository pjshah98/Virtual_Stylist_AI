from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .outfit_generator import OutfitGenerator, OutfitRequest
from .color_service import ColorService
from ..models.model_loader import ModelLoader


@dataclass(frozen=True)
class RecommendationResponse:
    request: Dict[str, Any]
    outfits: List[Dict[str, Any]]


class RecommendationService:
    def __init__(self):
        self._model_loader = ModelLoader()
        self._color_service = ColorService()
        self._generator = OutfitGenerator(color_service=self._color_service)

    def presets(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "casual",
                "label": "Casual",
                "vibe": "Easy, everyday staples",
                "defaults": {"top": "Any", "bottom": "Any", "shoes": "Any"},
            },
            {
                "id": "streetwear",
                "label": "Streetwear",
                "vibe": "Bold layers + sneakers",
                "defaults": {"top": "Hoodie", "bottom": "Jeans", "shoes": "Sneakers"},
            },
            {
                "id": "business",
                "label": "Business",
                "vibe": "Crisp, polished silhouettes",
                "defaults": {"top": "Shirt", "bottom": "Trousers", "shoes": "Loafers"},
            },
            {
                "id": "formal",
                "label": "Formal",
                "vibe": "Sharper silhouettes",
                "defaults": {"top": "Shirt", "bottom": "Trousers", "shoes": "Oxford"},
            },
            {
                "id": "sporty",
                "label": "Sporty",
                "vibe": "Comfort-forward, on-the-move",
                "defaults": {"top": "T-shirt", "bottom": "Joggers", "shoes": "Sneakers"},
            },
            {
                "id": "minimalist",
                "label": "Minimalist",
                "vibe": "Clean neutrals + simple shapes",
                "defaults": {"top": "Shirt", "bottom": "Trousers", "shoes": "Loafers"},
            },
        ]

    def available_colors(self) -> List[str]:
        return self._color_service.available_colors()

    def recommend(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Payload contract (API):
        - top: string or "Any"
        - bottom: string or "Any"
        - shoes: string or "Any"
        - colors: list[str] (optional)
        - style: string (optional) ["Casual","Formal","Streetwear","Sporty","Minimalist"]
        - season: string (optional) ["Summer","Winter","Fall","Spring"]
        - preset: string (optional) (legacy shortcut; overlaps style)
        - seed: int (optional) to vary shuffles
        - limit: int (optional, default 5)
        """
        top = (payload.get("top") or "Any").strip()
        bottom = (payload.get("bottom") or "Any").strip()
        shoes = (payload.get("shoes") or "Any").strip()
        preset = (payload.get("preset") or "").strip() or None
        style = (payload.get("style") or "").strip() or None
        season = (payload.get("season") or "").strip() or None
        seed = payload.get("seed")
        colors = payload.get("colors") or []
        limit = payload.get("limit") or 5

        # If preset is provided and style is not, treat it as the style.
        if preset and not style:
            style = preset

        req = OutfitRequest(
            top=top,
            bottom=bottom,
            shoes=shoes,
            colors=colors,
            preset=preset,
            style=style,
            season=season,
            seed=int(seed) if seed is not None else None,
        )

        model, feature_names = self._model_loader.load()
        candidates = self._generator.generate(req, max_candidates=100)
        ranked = self._generator.rank_with_model(
            candidates=candidates,
            model=model,
            feature_names=feature_names,
            limit=int(limit),
            style=style,
            season=season,
        )

        return {
            "request": {
                "top": top,
                "bottom": bottom,
                "shoes": shoes,
                "colors": colors,
                "preset": preset,
                "style": style,
                "season": season,
                "seed": int(seed) if seed is not None else None,
                "limit": int(limit),
            },
            "outfits": ranked,
        }

