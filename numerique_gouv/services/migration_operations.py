from django.db.migrations.operations.base import Operation


class AlterModelBases(Operation):
    """
    State-only operation changing the parent classes of a model.

    Django has no built-in operation for this and the autodetector does not notice base changes,
    so a model whose parent changed keeps its old bases in the migration state. Historical models
    then join on a parent link that no longer exists in the database.
    """

    reduces_to_sql = False
    reversible = True

    def __init__(self, name: str, bases: tuple):
        self.name = name
        self.bases = bases

    def deconstruct(self):
        return self.__class__.__qualname__, [], {"name": self.name, "bases": self.bases}

    def state_forwards(self, app_label, state):
        model_key = (app_label, self.name.lower())
        state.models[model_key].bases = self.bases
        state.reload_model(*model_key, delay=False)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def describe(self):
        return f"Alter bases of {self.name}"
