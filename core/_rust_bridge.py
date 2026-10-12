"""
Jeweler 3D Studio - Rust Native Engine Bridge (C-ABI)
Safely loads the compiled native shared library if present, with graceful fallback.
"""

import ctypes
import os
import platform
import sys
from pathlib import Path
from typing import List, Optional, Tuple

_LIB: Optional[ctypes.CDLL] = None
_LOAD_ATTEMPTED = False


class ProngPositionC(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("rot_z_rad", ctypes.c_double),
        ("is_corner", ctypes.c_int),
    ]


class Point2DC(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]


class CutterLevelC(ctypes.Structure):
    _fields_ = [
        ("z_level", ctypes.c_double),
        ("radius_factor", ctypes.c_double),
    ]


def _find_lib_path() -> Optional[Path]:
    """Locates the platform-specific compiled Rust binary."""
    base_dir = Path(__file__).resolve().parent
    system = platform.system().lower()

    if system == "windows":
        lib_name = "jeweler_core.dll"
    elif system == "darwin":
        lib_name = "libjeweler_core.dylib"
    else:
        lib_name = "libjeweler_core.so"

    candidates = [
        base_dir / "bin" / lib_name,
        base_dir / lib_name,
        base_dir.parent / "crates" / "jeweler_core" / "target" / "release" / lib_name,
        base_dir.parent / "dist" / "bin" / lib_name,
    ]

    for p in candidates:
        if p.exists() and p.is_file():
            return p
    return None


def get_rust_lib() -> Optional[ctypes.CDLL]:
    """Returns the loaded native CDLL instance, or None if not built/found."""
    global _LIB, _LOAD_ATTEMPTED
    if _LOAD_ATTEMPTED:
        return _LIB

    _LOAD_ATTEMPTED = True
    lib_path = _find_lib_path()
    if not lib_path:
        return None

    try:
        lib = ctypes.CDLL(str(lib_path))
        lib.j3d_core_version.restype = ctypes.c_int
        lib.j3d_core_version.argtypes = []

        sig_common = [
            ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double,
            ctypes.c_double, ctypes.POINTER(ProngPositionC), ctypes.c_size_t,
        ]

        # Prongs
        lib.j3d_calc_round_prongs.restype = ctypes.c_int
        lib.j3d_calc_round_prongs.argtypes = sig_common

        lib.j3d_calc_oval_prongs.restype = ctypes.c_int
        lib.j3d_calc_oval_prongs.argtypes = sig_common

        lib.j3d_calc_rect_prongs.restype = ctypes.c_int
        lib.j3d_calc_rect_prongs.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int,
            ctypes.c_double, ctypes.POINTER(ProngPositionC), ctypes.c_size_t,
        ]

        sig_fancy = [
            ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double,
            ctypes.POINTER(ProngPositionC), ctypes.c_size_t,
        ]
        for fn_name in ["j3d_calc_marquise_prongs", "j3d_calc_pear_prongs",
                        "j3d_calc_heart_prongs", "j3d_calc_trillion_prongs"]:
            fn = getattr(lib, fn_name)
            fn.restype = ctypes.c_int
            fn.argtypes = sig_fancy

        lib.j3d_calc_v_prong_coords.restype = ctypes.c_int
        lib.j3d_calc_v_prong_coords.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double,
            ctypes.POINTER(Point2DC), ctypes.c_size_t,
        ]

        # Cutters
        lib.j3d_get_cut_outline.restype = ctypes.c_int
        lib.j3d_get_cut_outline.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.POINTER(Point2DC), ctypes.c_size_t,
        ]

        lib.j3d_get_cutter_levels.restype = ctypes.c_int
        lib.j3d_get_cutter_levels.argtypes = [ctypes.POINTER(CutterLevelC), ctypes.c_size_t]

        # Metrics
        lib.j3d_get_metal_density.restype = ctypes.c_double
        lib.j3d_get_metal_density.argtypes = [ctypes.c_int]

        lib.j3d_calc_mesh_weight.restype = ctypes.c_double
        lib.j3d_calc_mesh_weight.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double,
        ]

        _LIB = lib
        return _LIB
    except Exception:
        _LIB = None
        return None


def has_rust_engine() -> bool:
    """Returns True if the native Rust library is active and operational."""
    return get_rust_lib() is not None


# --- PRONGS API WRAPPERS ---

def _invoke_prongs_fn(fn_name: str, *args) -> Optional[List[Tuple[float, float, float, bool]]]:
    lib = get_rust_lib()
    if not lib:
        return None
    fn = getattr(lib, fn_name, None)
    if not fn:
        return None

    max_c = 16
    buf = (ProngPositionC * max_c)()
    written = fn(*args, buf, max_c)
    if written <= 0:
        return None
    return [(buf[i].x, buf[i].y, buf[i].rot_z_rad, bool(buf[i].is_corner)) for i in range(written)]


def calc_round_prongs(dim_x: float, dim_y: float, count: int, user_angle: float, dist: float):
    return _invoke_prongs_fn("j3d_calc_round_prongs", dim_x, dim_y, count, user_angle, dist)


def calc_oval_prongs(dim_x: float, dim_y: float, count: int, user_angle: float, dist: float):
    return _invoke_prongs_fn("j3d_calc_oval_prongs", dim_x, dim_y, count, user_angle, dist)


def calc_rect_prongs(dim_x: float, dim_y: float, count: int, is_cut_corner: bool, dist: float):
    return _invoke_prongs_fn("j3d_calc_rect_prongs", dim_x, dim_y, count, int(is_cut_corner), dist)


def calc_marquise_prongs(dim_x: float, dim_y: float, count: int, dist: float):
    return _invoke_prongs_fn("j3d_calc_marquise_prongs", dim_x, dim_y, count, dist)


def calc_pear_prongs(dim_x: float, dim_y: float, count: int, dist: float):
    return _invoke_prongs_fn("j3d_calc_pear_prongs", dim_x, dim_y, count, dist)


def calc_heart_prongs(dim_x: float, dim_y: float, count: int, dist: float):
    return _invoke_prongs_fn("j3d_calc_heart_prongs", dim_x, dim_y, count, dist)


def calc_trillion_prongs(dim_x: float, dim_y: float, count: int, dist: float):
    return _invoke_prongs_fn("j3d_calc_trillion_prongs", dim_x, dim_y, count, dist)


def calc_v_prong_coords(s: float, t: float, d: float) -> Optional[List[Tuple[float, float]]]:
    lib = get_rust_lib()
    if not lib:
        return None
    buf = (Point2DC * 6)()
    written = lib.j3d_calc_v_prong_coords(s, t, d, buf, 6)
    if written != 6:
        return None
    return [(buf[i].x, buf[i].y) for i in range(6)]


# --- CUTTERS API WRAPPERS ---

CUT_FAMILY_MAP = {
    "ROUND": 0,
    "PRINCESS": 1, "SQUARE": 1, "ASSCHER": 1, "FLANDERS": 1, "OCTAGON": 1,
    "BAGUETTE": 2, "EMERALD": 2, "RADIANT": 2,
    "OVAL": 3, "CUSHION": 3,
    "PEAR": 4,
    "MARQUISE": 5,
    "HEART": 6,
    "TRILLION": 7, "TRILLIANT": 7, "TRIANGLE": 7,
}


def get_cut_outline(cut_name: str, segments: int) -> Optional[List[Tuple[float, float]]]:
    lib = get_rust_lib()
    if not lib:
        return None
    family_id = CUT_FAMILY_MAP.get((cut_name or "").upper(), 0)
    max_pts = max(4, segments)
    buf = (Point2DC * max_pts)()
    written = lib.j3d_get_cut_outline(family_id, segments, buf, max_pts)
    if written <= 0:
        return None
    return [(buf[i].x, buf[i].y) for i in range(written)]


def get_cutter_levels() -> Optional[List[Tuple[float, float]]]:
    lib = get_rust_lib()
    if not lib:
        return None
    buf = (CutterLevelC * 6)()
    written = lib.j3d_get_cutter_levels(buf, 6)
    if written != 6:
        return None
    return [(buf[i].z_level, buf[i].radius_factor) for i in range(6)]


# --- METRICS API WRAPPERS ---

METAL_ID_MAP = {
    "GOLD_24K": 0,
    "GOLD_18K_YELLOW": 1,
    "GOLD_18K_WHITE": 2,
    "GOLD_14K": 3,
    "PLATINUM_950": 4,
    "SILVER_925": 5,
    "TITANIUM": 6,
}


def get_metal_density(metal_key: str) -> Optional[float]:
    lib = get_rust_lib()
    if not lib:
        return None
    metal_id = METAL_ID_MAP.get(metal_key, 1)
    return lib.j3d_get_metal_density(metal_id)


def calc_mesh_weight(raw_volume: float, unit_scale: float, metal_key: str, shrinkage: float = 1.0) -> Optional[float]:
    lib = get_rust_lib()
    if not lib:
        return None
    metal_id = METAL_ID_MAP.get(metal_key, 1)
    return lib.j3d_calc_mesh_weight(raw_volume, unit_scale, metal_id, shrinkage)
