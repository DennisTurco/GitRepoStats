from dataclasses import dataclass
from datetime import datetime

@dataclass
class PeriodFilter:
    start_date: datetime
    end_date: datetime

    def __str__(self) -> str:
        start_str = self.start_date.strftime("%d/%m/%Y") if self.start_date else "N/A"
        end_str = self.end_date.strftime("%d/%m/%Y") if self.end_date else "N/A"
        return f"{start_str} - {end_str}"
