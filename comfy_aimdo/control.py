"""comfy_aimdo.control shim — device init and runtime control."""

import logging
import torch

_log = logging.getLogger("comfy_aimdo.control")


def init(simple_vram_headroom=None, nvml_pressure=True):
    _log.info("[aimdo-shim] init() called (headroom=%s, nvml=%s)", simple_vram_headroom, nvml_pressure)


def init_devices(devices_and_headrooms=None):
    if devices_and_headrooms is None:
        return False
    devs = list(devices_and_headrooms)
    if not devs:
        return False
    _log.info("[aimdo-shim] init_devices() — %d device(s), pretending success", len(devs))
    return True


def analyze():
    pass


def set_log_debug():
    logging.getLogger("comfy_aimdo").setLevel(logging.DEBUG)


def set_log_detail():
    try:
        set_log_info()
    except AttributeError:
        set_log_info()


def set_log_info():
    logging.getLogger("comfy_aimdo").setLevel(logging.INFO)


def set_log_warning():
    logging.getLogger("comfy_aimdo").setLevel(logging.WARNING)


def set_log_error():
    logging.getLogger("comfy_aimdo").setLevel(logging.ERROR)


def set_log_critical():
    logging.getLogger("comfy_aimdo").setLevel(logging.CRITICAL)
