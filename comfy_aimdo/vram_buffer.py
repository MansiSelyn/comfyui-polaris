"""comfy_aimdo.vram_buffer shim — GPU staging buffers using torch.cuda."""

import logging
import torch

_log = logging.getLogger("comfy_aimdo.vram_buffer")


class VRAMBuffer:
    """GPU-side staging buffer backed by plain torch.cuda allocation."""

    def __init__(self, reservation_size, device_index):
        self._device = torch.device("cuda", device_index)
        self._reservation = reservation_size
        try:
            self._buffer = torch.empty(reservation_size, dtype=torch.uint8, device=self._device)
        except Exception:
            self._buffer = None

    def get(self, size, offset):
        if self._buffer is None:
            return None
        if offset + size > self._reservation:
            return None
        return ("vram_buf", self._buffer.data_ptr() + offset, size, self._device)

    def size(self):
        return self._reservation if self._buffer is not None else 0
