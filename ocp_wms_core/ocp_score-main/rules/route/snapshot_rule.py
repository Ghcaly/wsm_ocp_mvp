from domain.base_rule import BaseRule


class SnapshotRule(BaseRule):
    """Faithful Python port of C# SnapshotRule.
    
    Creates a snapshot of the current context state for later comparison
    or rollback operations.
    """

    def __init__(self):
        super().__init__()

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
        """Always execute - snapshot creation is always needed"""
        return True

    def execute(self, context, item_predicate=None, mounted_space_predicate=None):
        """C#: Execute - creates snapshot of context"""
        context.CreateSnapshot()
