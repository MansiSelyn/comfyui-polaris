"""sageattn3 shim — SageAttention3 is Blackwell-only, this just errors clearly."""


def sageattn3_blackwell(*args, **kwargs):
    raise NotImplementedError("SageAttention3 requires NVIDIA Blackwell (SM 10.x). This is a Polaris shim.")
