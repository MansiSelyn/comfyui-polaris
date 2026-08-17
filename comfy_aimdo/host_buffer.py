"""comfy_aimdo.host_buffer shim — pinned host memory using torch.cuda.pinned_memory."""

import ctypes
import logging
import mmap
import os
import torch

_log = logging.getLogger("comfy_aimdo.host_buffer")


class HostBuffer:
    """Pinned host memory buffer backed by torch.cuda.pinned_memory."""

    def __init__(self, initial_size=0, alignment=0, max_size=0):
        self._size = 0
        self._max_size = max_size
        self._alignment = max(alignment, 1)
        self._pin = None
        self._tensor = None

    @property
    def size(self):
        return self._size

    def extend(self, size, register=True):
        needed = self._size + size
        needed = ((needed + self._alignment - 1) // self._alignment) * self._alignment
        needed = min(needed, self._max_size) if self._max_size > 0 else needed
        if needed <= self._size:
            return
        try:
            new_tensor = torch.empty(needed, dtype=torch.uint8, pin_memory=True)
            if self._tensor is not None:
                n = min(self._size, needed)
                new_tensor[:n].copy_(self._tensor[:n], non_blocking=False)
            self._tensor = new_tensor
            self._size = needed
        except Exception as e:
            _log.warning("[aimdo-shim] HostBuffer.extend failed: %s", e)

    def truncate(self, offset, do_unregister=True):
        if offset >= self._size:
            self._tensor = None
            self._size = 0
        else:
            self._size = offset

    def read_file_slice(self, file_obj, file_offset, size, buf_offset, stream, device_ptr, device):
        try:
            file_obj.seek(file_offset)
            raw = file_obj.read(size)
            if raw and self._tensor is not None:
                tensor_data = torch.frombuffer(bytearray(raw), dtype=torch.uint8)
                end = min(buf_offset + len(tensor_data), self._size)
                actual = end - buf_offset
                if actual > 0:
                    self._tensor[buf_offset:buf_offset + actual] = tensor_data[:actual]
        except Exception as e:
            _log.warning("[aimdo-shim] read_file_slice failed: %s", e)

    def get_raw_address(self):
        if self._tensor is None:
            return 0
        return self._tensor.data_ptr()


def read_file_to_device(file_obj, offset, size, stream_ptr, destination_data_ptr, device_index, mark_cold):
    try:
        file_obj.seek(offset)
        raw = file_obj.read(size)
        if raw and destination_data_ptr:
            device = torch.device("cuda", device_index)
            host_tensor = torch.frombuffer(bytearray(raw), dtype=torch.uint8)
            gpu_tensor = torch.empty(len(raw), dtype=torch.uint8, device=device)
            gpu_tensor.copy_(host_tensor, non_blocking=False)
            ctypes.memmove(destination_data_ptr, gpu_tensor.data_ptr(), len(raw))
    except Exception as e:
        _log.warning("[aimdo-shim] read_file_to_device failed: %s", e)
