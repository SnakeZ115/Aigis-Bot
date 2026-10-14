"""
Herramientas de Aigis para consumir la API 
oficial de Steam
"""

from typing import Any
from config import config, logger
import aiohttp
import asyncio
import os
import json

ARCHIVO_CACHE = "steam_games.json"
steam_games_list = []


async def _fetch_json(url: str, params: dict | None = None) -> dict[str, Any] | None:
    """Realiza una petición HTTP asíncrona y retorna la respuesta en formato JSON."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json(content_type=None)
                else:
                    logger.warning(f"Error en la petición a Steam ({response.status})")
                    return None
    except Exception as e:
        logger.error(f"Error de conexión con Steam: {e}")
        return None


async def get_games():
    """
    Obtiene los juegos de Steam y los almacena en un archivo JSON
    """
    global steam_games_list

    if os.path.exists(ARCHIVO_CACHE):
        with open(ARCHIVO_CACHE, "r", encoding="utf-8") as f:
            steam_games_list = json.load(f)
        logger.info(f"Lista cargada desde archivo local: {len(steam_games_list)} juegos.")
        return

    url = f"{config.steam_url_api.rstrip('/')}/IStoreService/GetAppList/v1/"
    all_apps = []
    have_more_results = True
    last_appid = None

    logger.info("Descargando catálogo de juegos de Steam...")

    while have_more_results:
        params = {
            "key": config.steam_api_key,
            "max_results": 50000,
        }
        if last_appid:
            params["last_appid"] = last_appid

        data = await _fetch_json(url=url, params=params)
        if not data or "response" not in data:
            logger.error("Error al obtener respuesta de la API de Steam.")
            break

        res = data["response"]
        apps = res.get("apps", [])
        if not apps:
            break

        all_apps.extend(apps)
        have_more_results = res.get("have_more_results", False)
        last_appid = res.get("last_appid")
        logger.info(f"Descargados {len(all_apps)} juegos de Steam hasta ahora...")

        # Pausa de cortesía para no saturar el rate limit de Steam
        if have_more_results:
            await asyncio.sleep(1.0)

    if all_apps:
        steam_games_list = all_apps
        with open(ARCHIVO_CACHE, "w", encoding="utf-8") as f:
            json.dump(steam_games_list, f, ensure_ascii=False)
        logger.info(f"Catálogo completo guardado en {ARCHIVO_CACHE}: {len(steam_games_list)} juegos.")
    else:
        logger.warning("No se pudo obtener ningún juego de Steam.")
    



def _normalize_name(text: str) -> str:
    """Elimina caracteres no alfanuméricos para tolerar variaciones en títulos."""
    import re
    return re.sub(r"[^a-z0-9]", "", text.lower())


def search_game_by_name(query: str) -> dict | None:
    """
    Busca un juego por nombre dentro del catálogo de Steam.
    Retorna el diccionario del juego {'appid': int, 'name': str, ...} o None si no existe.
    """
    global steam_games_list

    # Si aún no está en memoria, cargarlo desde el archivo local
    if not steam_games_list and os.path.exists(ARCHIVO_CACHE):
        with open(ARCHIVO_CACHE, "r", encoding="utf-8") as f:
            steam_games_list = json.load(f)

    if not steam_games_list:
        logger.warning("No hay lista de juegos cargada en memoria ni en disco.")
        return None

    q_clean = query.strip().lower()
    q_norm = _normalize_name(query)

    if not q_norm:
        return None

    # 1. Coincidencia exacta directa o normalizada
    for game in steam_games_list:
        name = game.get("name", "")
        if name.lower() == q_clean or _normalize_name(name) == q_norm:
            return game

    # 2. Coincidencia por subcadena
    candidates = []
    for game in steam_games_list:
        name_lower = game.get("name", "").lower()
        if q_clean in name_lower:
            candidates.append(game)

    # Si no hubo por texto directo, probar por subcadena normalizada
    if not candidates:
        for game in steam_games_list:
            if q_norm in _normalize_name(game.get("name", "")):
                candidates.append(game)

    # Si encontramos varios candidatos, elegimos el nombre más corto (más parecido al título principal)
    if candidates:
        candidates.sort(key=lambda x: len(x.get("name", "")))
        return candidates[0]

    return None


async def get_game_reviews(game_name: str) -> dict[str, Any]:
    """
    Busca un juego de Steam por nombre y obtiene sus estadísticas y reseñas más relevantes.
    """
    game = search_game_by_name(game_name)
    if not game:
        return {
            "success": False,
            "error": f"No se encontró ningún juego en Steam llamado '{game_name}'. Verifica el nombre del título."
        }

    appid = game["appid"]
    official_name = game["name"]
    logger.info("Obteniendo reseñas para '%s' (AppID: %s)...", official_name, appid)

    url = f"https://store.steampowered.com/appreviews/{appid}"
    params = {
        "json": 1,
        "language": "all",
        "num_per_page": 10,
        "purchase_type": "all",
    }

    data = await _fetch_json(url=url, params=params)
    if not data or not data.get("success"):
        return {
            "success": False,
            "error": f"No se pudieron consultar las reseñas de Steam para '{official_name}'."
        }

    summary = data.get("query_summary", {})
    total_reviews = summary.get("total_reviews", 0)
    total_positive = summary.get("total_positive", 0)
    total_negative = summary.get("total_negative", 0)
    score_desc = summary.get("review_score_desc", "Sin calificación")

    pos_pct = round((total_positive / total_reviews * 100), 1) if total_reviews > 0 else 0

    # Extraer muestra de reseñas y acotar texto para no saturar el contexto de Ollama
    sample_reviews = []
    for r in data.get("reviews", []):
        review_text = r.get("review", "").strip()
        if len(review_text) > 350:
            review_text = review_text[:350] + "..."

        sample_reviews.append({
            "is_positive": r.get("voted_up", True),
            "helpful_votes": r.get("votes_up", 0),
            "playtime_hours": round(r.get("author", {}).get("playtime_forever", 0) / 60, 1),
            "review": review_text,
        })

    return {
        "success": True,
        "game_name": official_name,
        "appid": appid,
        "rating_label": score_desc,
        "total_reviews": total_reviews,
        "positive_reviews": total_positive,
        "negative_reviews": total_negative,
        "approval_percentage": f"{pos_pct}%",
        "sample_reviews": sample_reviews,
    }