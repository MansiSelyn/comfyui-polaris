import logging
import torch

_POLARIS_ARCHS = ("gfx800", "gfx801", "gfx802", "gfx803", "gfx804", "gfx805", "gfx806")
_POLARIS_NAMES = ("RX 460", "RX 470", "RX 480", "RX 560", "RX 570", "RX 580", "RX 590")

_cached_arch = None
_cached_is_polaris = None


def _get_device_props():
    try:
        if not torch.cuda.is_available():
            return None
        return torch.cuda.get_device_properties(torch.cuda.current_device())
    except Exception:
        return None


def get_gcn_arch():
    global _cached_arch
    if _cached_arch is not None:
        return _cached_arch
    props = _get_device_props()
    if props is None:
        _cached_arch = ""
        return _cached_arch
    raw = getattr(props, "gcnArchName", "")
    _cached_arch = raw.split(":")[0].strip().lower()
    return _cached_arch


def is_polaris():
    global _cached_is_polaris
    if _cached_is_polaris is not None:
        return _cached_is_polaris
    arch = get_gcn_arch()
    if any(arch.startswith(a) for a in _POLARIS_ARCHS):
        _cached_is_polaris = True
        return True
    props = _get_device_props()
    if props is not None:
        name = getattr(props, "name", "")
        for target in _POLARIS_NAMES:
            if target.lower() in name.lower():
                _cached_is_polaris = True
                return True
    _cached_is_polaris = False
    return False


def is_zluda():
    try:
        return torch.version.cuda is not None and torch.version.hip is None
    except AttributeError:
        return False


def is_zluda_polaris():
    return is_zluda() and is_polaris()


def polaris_vram_mb():
    props = _get_device_props()
    if props is None:
        return 0
    return props.total_mem // (1024 * 1024)


def polaris_vram_bytes():
    props = _get_device_props()
    if props is None:
        return 0
    return props.total_mem


def log_polaris_info():
    if not is_polaris():
        return
    arch = get_gcn_arch()
    vram = polaris_vram_mb()
    backend = "ZLUDA" if is_zluda() else "native" if torch.version.hip else "DirectML/other"
    logging.info(
        "[polaris] Detected Polaris GPU: arch=%s VRAM=%dMB backend=%s",
        arch, vram, backend,
    )
