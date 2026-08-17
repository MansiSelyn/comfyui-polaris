"""comfy_aimdo.model_vbar shim — virtual buffer allocation using torch.cuda."""

import logging
import threading
import torch

_log = logging.getLogger("comfy_aimdo.model_vbar")

_lock = threading.Lock()


class _VbarSlot:
    __slots__ = ("data", "offset", "size", "pinned", "device")

    def __init__(self, data, offset, size, device):
        self.data = data
        self.offset = offset
        self.size = size
        self.pinned = False
        self.device = device


class ModelVBAR:
    """Replaces CUDA virtual memory reservations with plain torch.cuda allocation."""

    def __init__(self, size, device_index):
        self._device = torch.device("cuda", device_index)
        self._slots = []
        self._total_size = 0
        self._alloc_size = 0
        self._size = size

    def loaded_size(self):
        return self._alloc_size

    def prioritize(self):
        pass

    def alloc(self, size):
        data = torch.empty(size, dtype=torch.uint8, device=self._device)
        slot = _VbarSlot(data, 0, size, self._device)
        with _lock:
            self._slots.append(slot)
            self._alloc_size += size
            self._total_size += size
        return ("vbar", id(slot), slot)

    def free_memory(self, to_free):
        freed = 0
        with _lock:
            remaining = []
            for s in self._slots:
                if freed >= to_free:
                    remaining.append(s)
                    continue
                freed += s.size
                del s.data
            self._slots = remaining
            self._alloc_size -= freed
        return freed


def vbar_fault(v):
    if v is None or not isinstance(v, tuple) or len(v) < 3:
        return None
    slot = v[2]
    if not isinstance(slot, _VbarSlot):
        return None
    return id(slot)


def vbar_signature_compare(a, b):
    return a is not None and a == b


def vbar_unpin(v):
    if v is not None and isinstance(v, tuple) and len(v) >= 3:
        slot = v[2]
        if isinstance(slot, _VbarSlot):
            slot.pinned = False


def vbars_analyze(device_index):
    return 0
