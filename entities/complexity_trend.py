from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ComplexityTrendData:
    """Represents aggregated complexity metrics for a time period (e.g., month)"""
    period: str  # ISO format YYYY-MM for month, YYYY-MM-DD for day, etc.
    date: datetime  # Start date of the period
    avg_ccn: float  # Average cyclomatic complexity
    avg_nloc: float  # Average number of lines of code
    avg_token: float  # Average token count
    avg_param: float  # Average parameter count
    function_count: int  # Number of functions analyzed in this period
    total_ccn: float = 0  # Total CCN for this period
    total_nloc: float = 0  # Total NLOC for this period

    def __str__(self) -> str:
        return f"Period: {self.period}, Avg CCN: {self.avg_ccn:.2f}, Avg NLOC: {self.avg_nloc:.2f}, Functions: {self.function_count}"

    def to_csv(self) -> str:
        return f"{self.period},{self.avg_ccn:.2f},{self.avg_nloc:.2f},{self.avg_token:.2f},{self.avg_param:.2f},{self.function_count}"

    @staticmethod
    def csv_header() -> str:
        return "Period,AvgCCN,AvgNLOC,AvgToken,AvgParam,FunctionCount"

    @staticmethod
    def to_csv_data_list(trends: list["ComplexityTrendData"], header: bool = True) -> list[str]:
        data = [ComplexityTrendData.csv_header()] if header else []
        data += [trend.to_csv() for trend in trends]
        return data

    @staticmethod
    def sort_by_date(trends: list["ComplexityTrendData"]) -> None:
        trends.sort(key=lambda t: t.date)


@dataclass
class CommitComplexityData:
    """Represents complexity metrics at a specific commit"""
    commit_hash: str
    commit_date: datetime
    file_path: str
    function_name: str
    ccn: int
    nloc: int
    token: int
    param: int
    length: int

    def __str__(self) -> str:
        return f"Commit: {self.commit_hash[:8]}, File: {self.file_path}, Func: {self.function_name}, CCN: {self.ccn}"

    def to_csv(self) -> str:
        return f"{self.commit_hash},{self.commit_date.strftime('%Y-%m-%d')},{self.file_path},{self.function_name},{self.ccn},{self.nloc},{self.token},{self.param},{self.length}"

    @staticmethod
    def csv_header() -> str:
        return "CommitHash,Date,FilePath,FunctionName,CCN,NLOC,Token,Param,Length"

    @staticmethod
    def to_csv_data_list(data: list["CommitComplexityData"], header: bool = True) -> list[str]:
        csv_lines = [CommitComplexityData.csv_header()] if header else []
        csv_lines += [d.to_csv() for d in data]
        return csv_lines

    @staticmethod
    def sort_by_date(data: list["CommitComplexityData"]) -> None:
        data.sort(key=lambda d: d.commit_date)
