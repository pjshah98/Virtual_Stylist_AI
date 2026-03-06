from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd
import random

from .color_service import ColorService


@dataclass(frozen=True)
class OutfitRequest:
    top: str
    bottom: str
    shoes: str
    colors: List[str]
    preset: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None
    seed: Optional[int] = None


class OutfitGenerator:
    def __init__(self, color_service: ColorService):
        self._colors = color_service

        # A curated, “product-like” vocabulary. This is also aligned with the dataset/forms.
        self._top_options = [
            "Shirt",
            "T-shirt",
            "Blouse",
            "Hoodie",
            "Sweater",
            "Jacket",
            "Tank top",
            "Polo",
            "Cardigan",
            "Vest",
        ]
        self._bottom_options = [
            "Jeans",
            "Shorts",
            "Skirt",
            "Trousers",
            "Leggings",
            "Sweatpants",
            "Chinos",
            "Capris",
            "Joggers",
            "Culottes",
        ]
        self._shoes_options = [
            "Sneakers",
            "Boots",
            "Flats",
            "Heels",
            "Sandals",
            "Loafers",
            "Moccasins",
            "Derby",
            "Oxford",
            "Brogue",
        ]

        self._style_priority = {
            # Style preference / preset influence (requested examples).
            "streetwear": {
                "top": {"Hoodie": 3.0},
                "bottom": {"Joggers": 3.0, "Jeans": 2.0},
                "shoes": {"Sneakers": 3.0},
            },
            "business": {
                "top": {"Shirt": 3.0},
                "bottom": {"Trousers": 3.0, "Chinos": 2.0},
                "shoes": {"Loafers": 2.5, "Oxford": 2.5, "Derby": 2.0},
            },
            "formal": {
                "top": {"Shirt": 2.5},
                "bottom": {"Trousers": 2.5},
                "shoes": {"Oxford": 2.5, "Derby": 2.0},
            },
            "sporty": {
                "top": {"T-shirt": 2.5, "Tank top": 2.0, "Hoodie": 1.8},
                "bottom": {"Joggers": 3.0, "Sweatpants": 2.5, "Shorts": 2.0},
                "shoes": {"Sneakers": 3.0},
            },
            "minimalist": {
                "top": {"Shirt": 2.2, "Sweater": 1.6},
                "bottom": {"Trousers": 2.2, "Jeans": 1.2},
                "shoes": {"Loafers": 2.0, "Flats": 1.6, "Oxford": 1.6},
            },
            "casual": {},
        }

        self._season_priority = {
            "summer": {
                "top": {"Tank top": 2.4, "T-shirt": 1.8, "Polo": 1.6},
                "bottom": {"Shorts": 2.6, "Skirt": 1.8, "Capris": 1.6},
                "shoes": {"Sandals": 2.4, "Sneakers": 1.4},
            },
            "winter": {
                "top": {"Hoodie": 2.2, "Sweater": 2.2, "Jacket": 2.4, "Cardigan": 1.8},
                "bottom": {"Jeans": 1.6, "Trousers": 1.6, "Leggings": 1.5},
                "shoes": {"Boots": 2.6},
            },
            "fall": {
                "top": {"Jacket": 2.2, "Sweater": 1.8, "Hoodie": 1.5},
                "bottom": {"Jeans": 2.0, "Trousers": 1.4},
                "shoes": {"Boots": 2.2, "Loafers": 1.4},
            },
            "spring": {
                "top": {"Blouse": 2.0, "Cardigan": 1.8, "Shirt": 1.4},
                "bottom": {"Skirt": 2.0, "Jeans": 1.4, "Culottes": 1.4},
                "shoes": {"Flats": 2.0, "Sneakers": 1.4},
            },
        }

    def _apply_preset_defaults(self, req: OutfitRequest) -> OutfitRequest:
        if not req.preset:
            return req

        preset = req.preset.lower()
        if preset == "streetwear":
            return OutfitRequest(
                top=req.top if req.top != "Any" else "Hoodie",
                bottom=req.bottom if req.bottom != "Any" else "Jeans",
                shoes=req.shoes if req.shoes != "Any" else "Sneakers",
                colors=req.colors,
                preset=req.preset,
            )
        if preset == "formal":
            return OutfitRequest(
                top=req.top if req.top != "Any" else "Shirt",
                bottom=req.bottom if req.bottom != "Any" else "Trousers",
                shoes=req.shoes if req.shoes != "Any" else "Oxford",
                colors=req.colors,
                preset=req.preset,
            )
        if preset == "athleisure":
            return OutfitRequest(
                top=req.top if req.top != "Any" else "T-shirt",
                bottom=req.bottom if req.bottom != "Any" else "Joggers",
                shoes=req.shoes if req.shoes != "Any" else "Sneakers",
                colors=req.colors,
                preset=req.preset,
            )
        if preset == "business":
            return OutfitRequest(
                top=req.top if req.top != "Any" else "Shirt",
                bottom=req.bottom if req.bottom != "Any" else "Trousers",
                shoes=req.shoes if req.shoes != "Any" else "Loafers",
                colors=req.colors,
                preset=req.preset,
                style=req.style,
                season=req.season,
                seed=req.seed,
            )
        if preset == "minimalist":
            return OutfitRequest(
                top=req.top if req.top != "Any" else "Shirt",
                bottom=req.bottom if req.bottom != "Any" else "Trousers",
                shoes=req.shoes if req.shoes != "Any" else "Loafers",
                colors=req.colors,
                preset=req.preset,
                style=req.style,
                season=req.season,
                seed=req.seed,
            )
        if preset == "sporty":
            return OutfitRequest(
                top=req.top if req.top != "Any" else "T-shirt",
                bottom=req.bottom if req.bottom != "Any" else "Joggers",
                shoes=req.shoes if req.shoes != "Any" else "Sneakers",
                colors=req.colors,
                preset=req.preset,
                style=req.style,
                season=req.season,
                seed=req.seed,
            )
        # casual/default
        return req

    def _weighted_choice(self, options: List[str], weights: Dict[str, float], rng: random.Random) -> str:
        scored = []
        total = 0.0
        for o in options:
            w = float(weights.get(o, 1.0))
            if w <= 0:
                continue
            scored.append((o, w))
            total += w
        if not scored:
            return rng.choice(options)
        r = rng.random() * total
        upto = 0.0
        for o, w in scored:
            upto += w
            if upto >= r:
                return o
        return scored[-1][0]

    def _merged_weights(self, req: OutfitRequest) -> Dict[str, Dict[str, float]]:
        style_key = (req.style or req.preset or "casual").lower()
        season_key = (req.season or "").lower()

        weights = {"top": {}, "bottom": {}, "shoes": {}}
        for src in (self._style_priority.get(style_key, {}), self._season_priority.get(season_key, {})):
            for k in ("top", "bottom", "shoes"):
                for item, w in (src.get(k, {}) or {}).items():
                    weights[k][item] = max(weights[k].get(item, 1.0), float(w))
        return weights

    def generate(self, req: OutfitRequest, max_candidates: int = 100) -> List[Dict[str, Any]]:
        req = self._apply_preset_defaults(req)

        rng = random.Random(req.seed if req.seed is not None else random.randrange(0, 2**31 - 1))

        tops = self._top_options if req.top == "Any" else [req.top]
        bottoms = self._bottom_options if req.bottom == "Any" else [req.bottom]
        shoes = self._shoes_options if req.shoes == "Any" else [req.shoes]

        preferred_colors = [c for c in (req.colors or []) if c in self._colors.available_colors()]
        base_color = None
        for c in preferred_colors:
            if c not in {"Black", "White", "Gray"}:
                base_color = c
                break
        base_color = base_color or (preferred_colors[0] if preferred_colors else rng.choice(self._colors.available_colors()))

        # Choose a harmony mode. Minimalist leans monochromatic; otherwise complementary/analogous.
        style_key = (req.style or req.preset or "casual").lower()
        if style_key == "minimalist":
            mode = "monochromatic"
        else:
            mode = "complementary" if rng.random() < 0.7 else "analogous"

        palette_seed = self._colors.get_harmonious_colors(base_color, mode=mode, include_neutrals=True)
        palette = self._colors.suggest_palette(preferred_colors or palette_seed, k=3).palette
        if len(palette) < 3:
            for c in ["Black", "White", "Gray"]:
                if c not in palette and len(palette) < 3:
                    palette.append(c)

        weights = self._merged_weights(req)

        seen = set()
        candidates: List[Dict[str, Any]] = []
        attempts = 0
        max_attempts = max_candidates * 12
        while len(candidates) < max_candidates and attempts < max_attempts:
            attempts += 1
            top = self._weighted_choice(tops, weights["top"], rng)
            bottom = self._weighted_choice(bottoms, weights["bottom"], rng)
            shoe = self._weighted_choice(shoes, weights["shoes"], rng)

            # rotate palette; occasionally swap to create variety
            rotation = rng.randrange(0, 3)
            top_color = palette[(0 + rotation) % 3]
            bottom_color = palette[(1 + rotation) % 3]
            shoes_color = palette[(2 + rotation) % 3]
            if rng.random() < 0.22:
                top_color, bottom_color = bottom_color, top_color

            key = (top, bottom, shoe, top_color, bottom_color, shoes_color)
            if key in seen:
                continue
            seen.add(key)

            colors = [top_color, bottom_color, shoes_color]
            candidates.append(
                {
                    "items": {"top": top, "bottom": bottom, "shoes": shoe},
                    "colors": {"top": top_color, "bottom": bottom_color, "shoes": shoes_color},
                    "harmony_score": self._colors.harmony_score(colors),
                }
            )

        return candidates

    def _to_feature_row(self, outfit: Dict[str, Any]) -> Dict[str, Any]:
        items = outfit["items"]
        colors = outfit["colors"]

        row: Dict[str, Any] = {
            "top_wear": items["top"],
            "bottom_wear": items["bottom"],
            "shoes": items["shoes"],
        }

        # The training notebook used one-hot dummies for these fixed color names.
        selected = set([colors["top"], colors["bottom"], colors["shoes"]])
        for c in self._colors.available_colors():
            row[c] = 1 if c in selected else 0

        return row

    def rank_with_model(
        self,
        candidates: List[Dict[str, Any]],
        model,
        feature_names: List[str],
        limit: int = 5,
        style: Optional[str] = None,
        season: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        rows = [self._to_feature_row(o) for o in candidates]
        df = pd.DataFrame(rows)
        df = pd.get_dummies(df).reindex(columns=feature_names, fill_value=0)

        # Binary classifier → probability for class “1” becomes our ML score.
        proba = model.predict_proba(df)
        if proba.shape[1] == 1:
            ml_scores = proba[:, 0]
        else:
            ml_scores = proba[:, 1]

        ranked: List[Dict[str, Any]] = []
        for outfit, ml in zip(candidates, ml_scores):
            harmony = float(outfit.get("harmony_score") or 0.0)
            score = float(ml)
            score += 0.08 * harmony
            score += self._style_boost(outfit, style=style, season=season)
            ranked.append(
                {
                    "id": self._stable_outfit_id(outfit),
                    "items": outfit["items"],
                    "colors": outfit["colors"],
                    "ml_score": float(ml),
                    "harmony_score": harmony,
                    "score": score,
                    "label": self._label(outfit),
                }
            )

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[: max(1, int(limit))]

    def _style_boost(self, outfit: Dict[str, Any], style: Optional[str], season: Optional[str]) -> float:
        """
        Small additive boost to reflect style/season priorities (without overriding ML ranking).
        """
        boost = 0.0
        items = outfit.get("items") or {}
        colors = outfit.get("colors") or {}

        style_key = (style or "").lower()
        if style_key and style_key in self._style_priority:
            pri = self._style_priority[style_key]
            boost += 0.02 if items.get("top") in (pri.get("top") or {}) else 0.0
            boost += 0.02 if items.get("bottom") in (pri.get("bottom") or {}) else 0.0
            boost += 0.02 if items.get("shoes") in (pri.get("shoes") or {}) else 0.0

        if style_key == "minimalist":
            # Favor neutral palettes.
            if colors.get("top") in {"Black", "White", "Gray"}:
                boost += 0.015
            if colors.get("bottom") in {"Black", "White", "Gray"}:
                boost += 0.015
            if colors.get("shoes") in {"Black", "White", "Gray"}:
                boost += 0.015

        season_key = (season or "").lower()
        if season_key and season_key in self._season_priority:
            pri = self._season_priority[season_key]
            boost += 0.012 if items.get("top") in (pri.get("top") or {}) else 0.0
            boost += 0.012 if items.get("bottom") in (pri.get("bottom") or {}) else 0.0
            boost += 0.012 if items.get("shoes") in (pri.get("shoes") or {}) else 0.0

        return boost

    def _label(self, outfit: Dict[str, Any]) -> str:
        items = outfit["items"]
        colors = outfit["colors"]
        return (
            f'{colors["top"]} {items["top"]} · {colors["bottom"]} {items["bottom"]} · '
            f'{colors["shoes"]} {items["shoes"]}'
        )

    def _stable_outfit_id(self, outfit: Dict[str, Any]) -> str:
        items = outfit["items"]
        colors = outfit["colors"]
        raw = (
            f'{items["top"]}|{items["bottom"]}|{items["shoes"]}|'
            f'{colors["top"]}|{colors["bottom"]}|{colors["shoes"]}'
        )
        # Cheap stable hash (no crypto) for client-side keys.
        h = 0
        for ch in raw:
            h = (h * 31 + ord(ch)) % 1_000_000_007
        return f"o{h}"

