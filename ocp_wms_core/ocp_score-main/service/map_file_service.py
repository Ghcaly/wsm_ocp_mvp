"""Small MapFileService for saving PalletizeResultEvent JSON to disk.

This mirrors the responsibility of the C# MapFileService.SavePalletizeReportOnStorageAsync
in a minimal local form: serialize the event to JSON and save it to a file path.
"""
from typing import Dict, Any, Optional
import json
from pathlib import Path


def save_palletize_report_on_storage(event: Dict[str, Any], path: Optional[str] = None) -> str:
    """Serialize event dict and save to a local file.

    If `path` is provided it will be used; otherwise a default filename is created.
    Returns the path written as string.
    """
    if path:
        p = Path(path)
    else:
        # default filename
        p = Path(f"palletize_result_{event.get('UniqueKey', 'result')}.json")

    # Ensure parent exists
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)

    return str(p.resolve())
