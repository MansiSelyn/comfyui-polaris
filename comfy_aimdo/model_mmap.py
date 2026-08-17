"""comfy_aimdo.model_mmap shim — memory-mapped model loading using stdlib mmap."""

import ctypes
import logging
import mmap
import os

_log = logging.getLogger("comfy_aimdo.model_mmap")


class ModelMMAP:
    """Memory-mapped model file using Python's mmap module."""

    def __init__(self, ckpt_path):
        self._path = ckpt_path
        self._file = None
        self._mmap = None
        self._size = 0
        try:
            self._size = os.path.getsize(ckpt_path)
            self._file = open(ckpt_path, "rb")
            self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        except Exception as e:
            _log.warning("[aimdo-shim] ModelMMAP failed for %s: %s", ckpt_path, e)

    def get_file_handle(self):
        return self._file

    def get(self):
        if self._mmap is None:
            return 0
        try:
            buf = (ctypes.c_uint8 * self._size).from_buffer(self._mmap)
            return ctypes.addressof(buf)
        except Exception:
            return 0

    def __del__(self):
        try:
            if self._mmap is not None:
                self._mmap.close()
            if self._file is not None:
                self._file.close()
        except Exception:
            pass
