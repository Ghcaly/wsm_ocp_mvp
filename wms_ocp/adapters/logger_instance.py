# from .logger_system import JsonStepLogger

# logger = JsonStepLogger() 
from contextvars import ContextVar
from .logger_system import JsonStepLogger
from pathlib import Path
from typing import Optional

_current_logger: ContextVar[Optional[JsonStepLogger]] = ContextVar("_current_logger", default=None)
_global_logger = JsonStepLogger()  # fallback para scripts/CLI

def get_logger() -> JsonStepLogger:
    l = _current_logger.get()
    return l if l is not None else _global_logger

def set_logger(l: JsonStepLogger):
    _current_logger.set(l)

def clear_logger():
    _current_logger.set(None)

class _LoggerProxy:
    def __getattr__(self, name):
        return getattr(get_logger(), name)

# compat: importar `logger` continua funcionando em todo o código
logger = _LoggerProxy()
