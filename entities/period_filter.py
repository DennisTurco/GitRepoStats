from datetime import datetime

class PeriodFilter:
    start_date: datetime
    end_date: datetime

    def __init__(self, start_date: datetime, end_date: datetime) -> None:
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self) -> str:
        start_str = self.start_date.strftime("%d/%m/%Y") if self.start_date else "N/A"
        end_str = self.end_date.strftime("%d/%m/%Y") if self.end_date else "N/A"
        return f"{start_str} - {end_str}"
