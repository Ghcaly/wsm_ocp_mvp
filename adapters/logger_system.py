# logger_system.py
from datetime import datetime
import json
from pathlib import Path
from typing import Optional, List, Any
from decimal import Decimal


class JsonStepLogger:
    _instance = None  # Singleton

    def __new__(cls, filepath="process_log.json"):
        if cls._instance is None:
            cls._instance = super(JsonStepLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, filepath="process_log.json"):
        if self._initialized:
            return

        self.filepath = Path(filepath)
        self.steps = []
        self.current_step = None
        self.start_date = datetime.utcnow().isoformat()
        self._initialized = True

    # ---------------------------------------------------------------
    # UNIVERSAL SAFE SERIALIZER (resolve todos JSON errors)
    # ---------------------------------------------------------------
    def _safe(self, obj):
        """Converte qualquer coisa para JSON-serializável."""

        # Tipos já JSON-safe
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj

        # Decimal → float
        if isinstance(obj, Decimal):
            return float(obj)

        # datetime → ISO string
        if isinstance(obj, datetime):
            return obj.isoformat()

        # list → aplicar _safe
        if isinstance(obj, list):
            return [self._safe(x) for x in obj]

        # dict → aplicar _safe
        if isinstance(obj, dict):
            return {k: self._safe(v) for k, v in obj.items()}

        # objeto com __dict__
        if hasattr(obj, "__dict__"):
            return {k: self._safe(v) for k, v in vars(obj).items() if not callable(v)}

        # fallback → string
        return str(obj)

    # ---------------------------------------------------------------
    # Serializadores específicos para produtos
    # ---------------------------------------------------------------
    def _serialize_product_base(self, pb: Any):
        if pb is None:
            return None

        return {
            "name": self._safe(getattr(pb, "name", None)),
            "gross_weight": self._safe(getattr(pb, "gross_weight", None)),
            "code": self._safe(getattr(pb, "code", None)),
            "container_type": self._safe(getattr(pb, "ContainerType", None)),
        }

    def _serialize_product(self, p: Any):
        if p is None:
            return None

        product_obj = getattr(p, "Product", None)

        return {
            "Amount": self._safe(getattr(p, "Amount", None)),
            "name": self._safe(getattr(product_obj, "Name", None)),
            "gross_weight": self._safe(getattr(product_obj, "gross_weight", None)),
            "code": self._safe(getattr(product_obj, "code", None)),
            "container_type": self._safe(getattr(product_obj, "ContainerType", None)),
        }

    # ---------------------------------------------------------------
    # Serializa container
    # ---------------------------------------------------------------
    def _serialize_container(self, container: Any):
        products = getattr(container, "_products", [])
        product_base = getattr(container, "_product_base", None)

        return {
            "bulk": self._safe(getattr(container, "Bulk", None)),
            "blocked": self._safe(getattr(container, "Blocked", None)),
            "product_base": self._serialize_product_base(product_base),
            "products": [self._serialize_product(p) for p in products]
        }

    # ---------------------------------------------------------------
    def start_step(self, sequence: int, rule: str, step_type: str = None, registers=None):
        self.current_step = {
            "sequence": sequence,
            "rule": rule,
            "type": step_type,
            "registers": registers,
            "start_date": datetime.utcnow().isoformat(),
            "end_date": None,
            "executed": False,
            "mounted_spaces": [],
            "logs": [],
            "raw": {
                "Rule": rule,
                "Logs": [],
                "Children": [],
                "Debug": None
            }
        }

    def log(self, message: str):
        if not self.current_step:
            raise RuntimeError("Nenhum passo iniciado. Use start_step() antes.")

        self.current_step["logs"].append(message)
        self.current_step["raw"]["Logs"].append(message)

    def end_step(self, executed: bool = True, mounted_spaces: Optional[List[Any]] = None):

        if self.current_step:

            self.current_step["end_date"] = datetime.utcnow().isoformat()
            self.current_step["executed"] = executed

            if mounted_spaces:
                out_spaces = []

                for ms in mounted_spaces:
                    containers = getattr(ms, "_containers", [])
                    weight = getattr(ms, "Weight", None)

                    out_spaces.append({
                        "weight": self._safe(weight),
                        "containers": [
                            self._serialize_container(c) for c in containers
                        ]
                    })

                # self.current_step["mounted_spaces"] = out_spaces

            self.steps.append(self.current_step)
            self.current_step = None

    def save(self, filepath: Optional[str] = None):
        """
        Save the accumulated steps to JSON.

        If `filepath` is provided and is a directory, the logger file
        `process_log.json` will be written inside that directory. If
        `filepath` is a file path, it will be used as the destination file.
        If not provided, the original `self.filepath` is used.
        """
        if self.current_step:
            self.end_step(executed=False)

        final_data = self._safe({
            "start_date": self.start_date,
            "end_date": datetime.utcnow().isoformat(),
            "steps": self.steps
        })

        # determine destination path
        dest = Path(filepath) if filepath is not None else self.filepath

        # if a directory was provided (or path has no suffix), place file inside it
        try:
            if dest.exists() and dest.is_dir():
                dest = dest / self.filepath.name
            else:
                # treat paths without suffix as directories
                if dest.suffix == '':
                    dest = dest / self.filepath.name
        except Exception:
            # fallback: use configured filepath
            dest = self.filepath

        # ensure parent exists
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        with dest.open("w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)

        # update stored filepath to the last saved location
        self.filepath = dest

        return final_data
