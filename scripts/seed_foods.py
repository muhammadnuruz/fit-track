"""Taom bazasini urug'lash (seed) skripti — Bosqich 1.

Ikki manba (SPEC §5):
  1) Ochiq baza (USDA / Open Food Facts) — asosiy mahsulotlar.
  2) Qo'lda O'zbek taomlar — palov, somsa, mastava va h.k.

Hozircha placeholder: struktura tayyor, to'ldirish Bosqich 1 da.
Ishga tushirish:  python -m scripts.seed_foods
"""

from __future__ import annotations

import asyncio

from app.logging_config import get_logger, setup_logging

log = get_logger(__name__)

# Qo'lda kiritiladigan O'zbek taomlari (100g uchun). Bosqich 1 da kengaytiriladi.
# (nom, kcal, protein, carb, fat)
UZBEK_FOODS: list[tuple[str, float, float, float, float]] = [
    # ("Osh (palov)", 210, 6.0, 22.0, 11.0),
    # ("Somsa (go'shtli)", 280, 9.0, 27.0, 15.0),
    # ("Non (patir)", 260, 8.0, 50.0, 3.0),
]


async def seed() -> None:
    log.info("seed.start", uzbek_count=len(UZBEK_FOODS))
    # TODO(Bosqich 1): foods jadvaliga yozish + embedding hisoblash.
    log.info("seed.done")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(seed())
