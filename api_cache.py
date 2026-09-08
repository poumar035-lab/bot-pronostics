# -*- coding: utf-8 -*-
"""Cache disque avec TTL + gestionnaire de débit API (anti 429)."""
import json
import os
import time
import threading

CACHE_DIR = "apicache"
DEFAULT_TTL = 6 * 3600  # 6 heures par défaut

# Throttle : max N requêtes par fenêtre de 60 secondes (Safe pour plan gratuit)
MAX_CALLS_PER_MINUTE = 8
_lock = threading.Lock()
_calls_log = []  # timestamps des requêtes API réelles


def _cache_path(key):
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in ".-_" else "_" for c in key)
    return os.path.join(CACHE_DIR, f"{safe}.json")


def get_cached(key, ttl=DEFAULT_TTL):
    path = _cache_path(key)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if time.time() - data.get("ts", 0) < ttl:
            return data.get("value")
        return None
    except Exception:
        return None


def set_cached(key, value):
    path = _cache_path(key)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "value": value}, f, ensure_ascii=False)
    except Exception:
        pass


def throttle():
    """Attend si on a dépassé le quota glissant. Sérialise les appels."""
    with _lock:
        now = time.time()
        window_start = now - 60
        _calls_log[:] = [t for t in _calls_log if t > window_start]
        if len(_calls_log) >= MAX_CALLS_PER_MINUTE:
            wait = 60 - (now - _calls_log[0]) + 0.5
        else:
            wait = 0
    if wait > 0:
        time.sleep(max(wait, 0.5))
        with _lock:
            now = time.time()
            window_start = now - 60
            _calls_log[:] = [t for t in _calls_log if t > window_start]
    with _lock:
        _calls_log.append(time.time())


def fetch_json(url, headers, timeout=15, retries=3):
    """Requête HTTP avec throttle + retry + mise au cache gérée par l'appelant."""
    import requests

    throttle()
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                # Rate limité : attendre + long
                wait = 30 + attempt * 20
                time.sleep(wait)
                last_err = "rate_limit"
                continue
            # 403 => clé invalide / compétition non dispo
            if r.status_code in (403, 404):
                return None
            last_err = f"http_{r.status_code}"
            break
        except Exception as e:
            last_err = str(e)
            time.sleep(2 * (attempt + 1))
    return {"error": last_err} if last_err else None


def cached_request(key, url, headers, ttl=DEFAULT_TTL):
    """Récupère depuis le cache sinon appelle l'API et met en cache."""
    cached = get_cached(key, ttl)
    if cached is not None:
        return cached
    data = fetch_json(url, headers)
    if data is not None:
        if isinstance(data, dict) and "error" not in data:
            set_cached(key, data)
        else:
            # Cache négatif court pour les endpoints qui échouent (évite le re-call)
            set_cached(key + "_neg", {"error": "n/a"})
        return data
    # 404/403/None => cache négatif court pour ne pas re-caller
    set_cached(key + "_neg", {"error": "n/a"})
    return None