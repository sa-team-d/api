from typing import Dict, Any

class FilterParams:
    def __init__(self, filters: Dict[str, Any]):
        self.filters = filters

    def items(self):
        return self.filters.items()