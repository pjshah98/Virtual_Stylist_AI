from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple


@dataclass(frozen=True)
class HarmonyResult:
    palette: List[str]
    harmony: str
    score: float


class ColorService:
    """
    Lightweight color harmony engine (no external deps).
    Provides harmony scoring and palette suggestions based on a simplified color wheel.
    """

    _WHEEL = [
        "Red",
        "Orange",
        "Yellow",
        "Green",
        "Blue",
        "Purple",
        "Pink",
    ]

    _NEUTRALS = ["Black", "White", "Gray"]
    _COMPLEMENT: Dict[str, str] = {
        # Explicit rules requested.
        "Blue": "Orange",
        "Red": "Green",
        "Purple": "Yellow",
        # Reasonable additions.
        "Orange": "Blue",
        "Green": "Red",
        "Yellow": "Purple",
        "Pink": "Green",
    }

    def available_colors(self) -> List[str]:
        return ["Red", "Blue", "Black", "Green", "Yellow", "Pink", "White", "Gray", "Purple", "Orange"]

    def _idx(self, color: str) -> int | None:
        try:
            return self._WHEEL.index(color)
        except ValueError:
            return None

    def harmony_score(self, colors: List[str]) -> float:
        """
        Score in [0, 1]. Higher is better.
        - Neutrals always help.
        - Wheel-based distances prefer complementary/triadic/analogous patterns.
        """
        if not colors:
            return 0.0

        unique = list(dict.fromkeys([c for c in colors if c]))
        neutrals = [c for c in unique if c in self._NEUTRALS]
        wheel = [c for c in unique if c in self._WHEEL]

        if not wheel:
            return 0.6 if neutrals else 0.0

        idxs = sorted([self._idx(c) for c in wheel if self._idx(c) is not None])
        if len(idxs) == 1:
            base = 0.65
        else:
            # compute circular distances between consecutive colors
            n = len(self._WHEEL)
            dists = []
            for a, b in zip(idxs, idxs[1:]):
                d = min((b - a) % n, (a - b) % n)
                dists.append(d)
            # also wrap-around
            wrap = min((idxs[0] - idxs[-1]) % n, (idxs[-1] - idxs[0]) % n)
            dists.append(wrap)

            # reward common harmony distances: analogous (1), triadic (~2-3 on 7 wheel), complementary (~3)
            # on a 7-color wheel, complementary is distance 3.
            harmony_hits = sum(1 for d in dists if d in {1, 2, 3})
            base = min(0.9, 0.45 + 0.15 * harmony_hits)

        neutral_boost = 0.08 * min(2, len(neutrals))
        return max(0.0, min(1.0, base + neutral_boost))

    def get_harmonious_colors(
        self,
        base_color: str,
        mode: Literal["complementary", "analogous", "monochromatic"] = "complementary",
        include_neutrals: bool = True,
    ) -> List[str]:
        """
        Returns an ordered list of colors that pair well with `base_color`.
        This is intentionally simple/transparent (rule-based), and is used during outfit generation.
        """
        if base_color not in self.available_colors():
            return ["Black", "White", "Gray"] if include_neutrals else []

        if base_color in self._NEUTRALS:
            palette = [base_color]
            if include_neutrals:
                palette += [c for c in self._NEUTRALS if c != base_color]
            return palette

        palette: List[str] = [base_color]
        if mode == "complementary":
            comp = self._COMPLEMENT.get(base_color)
            if comp:
                palette.append(comp)
        elif mode == "analogous":
            idx = self._idx(base_color)
            if idx is not None:
                n = len(self._WHEEL)
                palette.append(self._WHEEL[(idx - 1) % n])
                palette.append(self._WHEEL[(idx + 1) % n])
        elif mode == "monochromatic":
            # Monochromatic: keep the base; neutrals do the rest.
            pass

        if include_neutrals:
            palette += self._NEUTRALS

        # De-dupe while preserving order.
        return list(dict.fromkeys([c for c in palette if c in self.available_colors()]))

    def suggest_palette(self, preferred: List[str], k: int = 3) -> HarmonyResult:
        preferred = [c for c in (preferred or []) if c in self.available_colors()]
        if not preferred:
            palette = ["Black", "White", "Gray"][:k]
            return HarmonyResult(palette=palette, harmony="neutral", score=self.harmony_score(palette))

        # If the user provides a single accent, build a complementary palette automatically.
        accents = [c for c in preferred if c not in self._NEUTRALS]
        neutrals = [c for c in preferred if c in self._NEUTRALS]

        if len(accents) == 1:
            base = accents[0]
            palette = self.get_harmonious_colors(base, mode="complementary", include_neutrals=True)
            palette = [c for c in palette if c in self.available_colors()]
            return HarmonyResult(palette=palette[:k], harmony="complementary", score=self.harmony_score(palette[:k]))

        # Otherwise: stable preference order (accents first, then neutrals).
        palette: List[str] = []
        for c in accents + neutrals:
            if c not in palette:
                palette.append(c)

        if len(palette) < k:
            for c in self._NEUTRALS:
                if len(palette) >= k:
                    break
                if c not in palette:
                    palette.append(c)

        return HarmonyResult(palette=palette[:k], harmony="preferred", score=self.harmony_score(palette[:k]))

