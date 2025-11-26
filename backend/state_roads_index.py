"""State Maintained Roads index helper.

This module loads the SA "State Maintained Roads" GeoJSON dataset
(Roads_GDA2020.geojson) and provides a simple lookup function to
answer: is this road state-maintained, and who is the authority?

We intentionally keep the logic simple and indexed by a normalized road
name key to avoid heavy geospatial processing in this environment.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "Roads_GDA2020.geojson")


def _normalize_name(name: Optional[str], roadtype: Optional[str]) -> Optional[str]:
    """Create a simple normalized key from name + roadtype.

    Examples:
      name='KING WILLIAM', roadtype='STREET' -> 'KING WILLIAM STREET'
      name='PORT WAKEFIELD', roadtype='ROAD' -> 'PORT WAKEFIELD ROAD'

    Returns uppercased key or None if no usable name.
    """
    if not name:
        return None
    name = name.strip().upper()
    if roadtype:
        roadtype = roadtype.strip().upper()
        return f"{name} {roadtype}"
    return name


@lru_cache(maxsize=1)
def load_state_roads_index() -> Dict[str, Dict[str, Any]]:
    """Load the state roads GeoJSON and build an index by normalized road name.

    Returns a dict: { normalized_name: { 'roaduseauthority': int, 'road_id': int|None, ... } }
    """
    index: Dict[str, Dict[str, Any]] = {}

    if not os.path.exists(DATA_PATH):
        # Dataset not available; return empty index
        return index

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # On any parse error, behave as if no index
        return index

    features = data.get("features", [])
    for feat in features:
        props = feat.get("properties", {}) or {}
        name = props.get("name")
        roadtype = props.get("roadtype")
        key = _normalize_name(name, roadtype)
        if not key:
            continue

        # Prefer entries with a non-null road_id (more authoritative)
        existing = index.get(key)
        if existing and existing.get("road_id") is not None:
            continue

        index[key] = {
            "name": name,
            "roadtype": roadtype,
            "class": props.get("class"),
            "surface": props.get("surface"),
            "routenum": props.get("routenum"),
            "roadusetype": props.get("roadusetype"),
            "roaduseauthority": props.get("roaduseauthority"),
            "road_id": props.get("road_id"),
            "crrs_road_no": props.get("crrs_road_no"),
            "tars_road_no": props.get("tars_road_no"),
        }

    return index


def lookup_state_road(road_name: str) -> Dict[str, Any]:
    """Lookup basic state-maintained road info by road name string.

    This is a *best-effort* text-based match; it does not use lat/lng geometry.

    Returns a dict like:
      {
        'is_state_maintained': bool,
        'authority_code': int | None,
        'authority_name': str | None,
        'road_id': int | None,
        'crrs_road_no': str | None,
        'tars_road_no': str | None,
      }
    """
    if not road_name:
        return {
            "is_state_maintained": False,
            "authority_code": None,
            "authority_name": None,
            "road_id": None,
            "crrs_road_no": None,
            "tars_road_no": None,
        }

    # Very simple normalization: make uppercase, strip extra spaces
    name = " ".join(road_name.upper().split())

    index = load_state_roads_index()

    # Direct match first
    info = index.get(name)
    if not info:
        # Try matching by just the base name (without roadtype suffix)
        parts = name.split()
        if len(parts) > 1:
            base = " ".join(parts[:-1])
            for key, value in index.items():
                if key.startswith(base):
                    info = value
                    break

    if not info:
        return {
            "is_state_maintained": False,
            "authority_code": None,
            "authority_name": None,
            "road_id": None,
            "crrs_road_no": None,
            "tars_road_no": None,
        }

    authority_code = info.get("roaduseauthority")
    # According to dataset conventions, roaduseauthority==7 often indicates DIT SA
    if authority_code == 7:
        authority_name = "SA DIT (State Maintained Road)"
        is_state = True
    else:
        authority_name = None
        is_state = False

    return {
        "is_state_maintained": is_state,
        "authority_code": authority_code,
        "authority_name": authority_name,
        "road_id": info.get("road_id"),
        "crrs_road_no": info.get("crrs_road_no"),
        "tars_road_no": info.get("tars_road_no"),
    }
