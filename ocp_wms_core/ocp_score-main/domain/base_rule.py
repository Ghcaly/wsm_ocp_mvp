from abc import ABC, abstractmethod


class BaseRule(ABC):
    """Base class for rules.

    Provides a C#-like `ExecuteChain` entry point that accepts optional
    predicates (item and mounted-space). Rules can keep implementing
    `execute(self, context)` for backwards compatibility; the
    `execute_chain` helper will call `should_execute` and then `execute`.
    """
    def __init__(self, name=None):
        self.name = name
    
    @abstractmethod
    def execute(self, context, item_predicate=None, mounted_space_predicate=None):
        """Execute the rule's logic.

        Existing implementations that only accept `context` will continue
        to work because callers provide only `context` and this method
        remains compatible.
        """
        pass

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None) -> bool:
        """Return whether this rule should run.

        Default is True. Concrete rules may override to inspect the
        context and provided predicates.
        """
        return True

