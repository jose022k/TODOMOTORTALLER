import re
import requests
import urllib3
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import BCV_URL, BCV_CACHE_MINUTES

# Constante clave de configuración para la tasa manual
TASA_MANUAL_KEY = "tasa_bcv_manual"

_cache: Optional[dict] = None


def _get_auto_tasa() -> Optional[float]:
    """Consulta la tasa de referencia del dólar directamente en bcv.org.ve."""
    try:
        urllib3.disable_warnings()
        resp = requests.get(
            BCV_URL,
            timeout=10,
            verify=False,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        html = resp.text
        m = re.search(r'<div id="dolar".*?strong-tb">\s*([\d.,]+)\s*<', html, re.S)
        if not m:
            return None
        return float(m.group(1).replace(".", "").replace(",", "."))
    except Exception:
        return None


def _read_manual_tasa(db: Session) -> Optional[float]:
    """Lee la tasa manual configurada por el admin desde la tabla configuracion."""
    try:
        row = db.execute(
            text("SELECT valor FROM configuracion WHERE clave = :clave"),
            {"clave": TASA_MANUAL_KEY},
        ).fetchone()
        if row:
            return float(row[0])
    except Exception:
        return None
    return None


def get_tasa(db: Session) -> Tuple[float, str]:
    """Devuelve (tasa, fuente). Prioriza auto con caché; fallback a manual."""
    global _cache

    now = datetime.now(timezone.utc)

    # 1. Usar caché si está vigente
    if _cache and now - _cache["ts"] < timedelta(minutes=BCV_CACHE_MINUTES):
        return _cache["tasa"], _cache["fuente"]

    # 2. Intentar consulta automática
    auto = _get_auto_tasa()
    if auto and auto > 0:
        _cache = {"tasa": auto, "fuente": "auto", "ts": now}
        return auto, "auto"

    # 3. Fallback a tasa manual
    manual = _read_manual_tasa(db)
    if manual and manual > 0:
        _cache = {"tasa": manual, "fuente": "manual", "ts": now}
        return manual, "manual"

    raise ValueError("No hay tasa BCV disponible. Configúrala manualmente en Reportes.")


def set_tasa_manual(db: Session, tasa: float):
    """Guarda (o actualiza) la tasa manual del admin."""
    db.execute(
        text(
            """
            INSERT INTO configuracion (clave, valor) VALUES (:clave, :valor)
            ON CONFLICT (clave) DO UPDATE SET valor = :valor
            """
        ),
        {"clave": TASA_MANUAL_KEY, "valor": str(tasa)},
    )
    db.commit()

    global _cache
    _cache = {"tasa": tasa, "fuente": "manual", "ts": datetime.now(timezone.utc)}


def convertir_a_usd(db: Session, monto: float, moneda: str) -> Tuple[float, Optional[float], str]:
    """Convierte un monto a USD según la moneda. Devuelve (monto_usd, tasa, fuente)."""
    moneda = moneda.upper()
    if moneda == "USD":
        return round(monto, 2), None, "usd"
    if moneda == "BS":
        tasa, fuente = get_tasa(db)
        return round(monto / tasa, 2), tasa, fuente
    raise ValueError("Moneda no válida. Use 'BS' o 'USD'.")
