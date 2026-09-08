"""Pytest umumiy sozlamalari."""

from __future__ import annotations

import os

# Testlar DB/token talab qilmasligi uchun muhitni oldindan belgilaymiz.
os.environ.setdefault("ENV", "test")
os.environ.setdefault("BOT_TOKEN", "test:token")
