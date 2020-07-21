import attr
import numpy as np
from typing import Dict, Any
from nexus_constructor.model.value_type import ValueType


@attr.s(eq=False)
class FieldAttribute:
    """
    Class for containing attributes in the nexus structure.
    Uses the long format (dict with "name" and "values" as keys) in the file-writer JSON format
    rather than the short form (name:value) as this works for everything and is more flexible, with
    the trade-off being a longer message (which is not a priority)
    """

    name = attr.ib(type=str)
    values = attr.ib(type=ValueType, cmp=False)
    type = attr.ib(type=str, default="String")

    def __eq__(self, other_attribute):
        if not self.name == other_attribute.name:
            return False
        if np.isscalar(self.values) or isinstance(self.values, list):
            return self.values == other_attribute.values
        return np.array_equal(self.values, other_attribute.values)

    def as_dict(self) -> Dict[str, Any]:
        values = self.values
        if isinstance(values, np.ndarray):
            values = values.tolist()
        return {"name": self.name, "type": self.type, "values": values}
