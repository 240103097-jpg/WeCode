"""Server-owned authored content, loaded at startup; no generated/new curriculum."""
from copy import deepcopy
import json
from pathlib import Path
from .contract import valid


class Curriculum:
    def __init__(self):
        data = json.loads((Path(__file__).resolve().parents[1] / 'data/curriculum.json').read_text())
        self._units = data['units']
        self._rules = data['answerRules']
        assert len(self._units) == 9
        assert all(valid('Unit', unit) for unit in self._units)
        self._by_id = {unit['id']: unit for unit in self._units}
        ids = [exercise['id'] for unit in self._units for exercise in unit['exercises']]
        assert len(ids) == len(set(ids)) == 27
        assert set(ids) == set(self._rules)

    def public_units(self):
        # Deliberately separate from rules; no ordinary read ever merges the two.
        return deepcopy(self._units)

    def has_unit(self, unit_id):
        return unit_id in self._by_id

    def rule(self, unit_id, exercise_id):
        unit = self._by_id.get(unit_id)
        if unit and any(exercise['id'] == exercise_id for exercise in unit['exercises']):
            return deepcopy(self._rules[exercise_id])
        return None
