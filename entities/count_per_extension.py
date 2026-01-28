from collections import defaultdict
from dataclasses import dataclass, field

@dataclass
class CountPerExtension:
    total: int = 0
    per_extension: dict[str, int] = field(default_factory=lambda: defaultdict(int))