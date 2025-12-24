"""Adapters package for ocp_score_ia.

This package exposes adapters that convert internal domain models (Context, Pallet,
MountedSpace, Produto, etc.) into the final event/DTO shape used by the StackBuilder
output (PalletizeResultEvent). The canonical adapter implemented here is the
PalletizeResultEvent adapter.
"""

from .palletize_result_event_adapter import build_palletize_result_event, to_json

__all__ = [
    "build_palletize_result_event",
    'to_json'
]
