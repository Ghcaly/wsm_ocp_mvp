from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any
# ...existing code...

@dataclass
class PalletizeDto:
    """Light DTO that holds input payload values used by the mapper/output generator."""
    unb_code: Any = None
    vehicle_plate: Any = None
    document_number: Any = None
    document_type: Any = None
    delivery_date: Any = None
    unique_key: Any = None  
    request: Dict[str, Any] = field(default_factory=dict)
    original_payload: Dict[str, Any] = field(default_factory=dict)
    spaces_payload: Any = None
    catalog_name: str = "Brasil"