#!/usr/bin/env bash
# Docker DB (pgvector) tayyor ekanligini kafolatlaydi:
#   1) Docker daemon ishlayotganini tekshiradi (o'chiq bo'lsa Docker Desktop'ni ochadi va kutadi)
#   2) db konteynerini ko'taradi
#   3) healthcheck 'healthy' bo'lguncha kutadi
# Har qanday qadamda muvaffaqiyatsizlik bo'lsa aniq xabar bilan chiqadi.
set -euo pipefail

CONTAINER="fittrack-db"

# --- 1) Docker daemon ---
if ! docker info >/dev/null 2>&1; then
  echo "🐳 Docker daemon ishlamayapti — Docker Desktop ochilmoqda..."
  open -a Docker >/dev/null 2>&1 || {
    echo "❌ Docker Desktop topilmadi. Iltimos, uni qo'lda oching."; exit 1;
  }
  printf "   daemon kutilmoqda"
  for _ in $(seq 1 60); do
    if docker info >/dev/null 2>&1; then echo " — tayyor ✅"; break; fi
    printf "."; sleep 2
  done
  if ! docker info >/dev/null 2>&1; then
    echo ""; echo "❌ Docker daemon 2 daqiqada ko'tarilmadi."; exit 1
  fi
fi

# --- 2) db konteyneri ---
docker compose up -d db >/dev/null

# --- 3) healthcheck ---
printf "🩺 DB sog'ligini kutish"
for _ in $(seq 1 30); do
  hs="$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null || echo starting)"
  if [ "$hs" = "healthy" ]; then echo " — healthy ✅"; exit 0; fi
  printf "."; sleep 2
done

echo ""; echo "❌ DB 60 soniyada 'healthy' bo'lmadi. Loglar:"
docker logs --tail 20 "$CONTAINER" 2>&1 || true
exit 1
