from enum import Enum
from dataclasses import dataclass, field

@dataclass
class LizardLocation():
    function: str
    lines: str
    file: str

class Status(Enum):
    HEALTHY = 1
    NEEDS_ATTENTION = 2
    AT_RISK = 3

    def to_emoji(self) -> str:
        return {
            Status.HEALTHY: "✅",
            Status.NEEDS_ATTENTION: "⚠️",
            Status.AT_RISK: "❌"
        }[self]

@dataclass
class LizardData():
    nloc: int # Number of Lines of Code
    ccn: int # Cyclomatic Complexity Number.(complex if > 10)
    token: int # code size metric
    param: int # params number
    length: int # function row length (similar to nloc but including declarations, exc...)
    location: LizardLocation # location function
    status: Status = field(init=False)

    def __post_init__(self):
        if self.nloc <= 30 and self.ccn <= 10 and self.token <= 100 and self.param <= 4:
            self.status = Status.HEALTHY
        elif self.nloc <= 100 and self.ccn <= 20 and self.token <= 500 and self.param <= 7:
            self.status = Status.NEEDS_ATTENTION
        else:
            self.status = Status.AT_RISK

    def to_csv(self) -> str:
        return f"{self.status.to_emoji()}|{self.nloc}|{self.ccn}|{self.token}|{self.param}|{self.length}|{self.location.function}|{self.location.lines}|{self.location.file}"

    @staticmethod
    def csv_header() -> str:
        return "Status|NLOC|CCN|Token|Param|Length|Function|Lines|File"

    @staticmethod
    def to_csv_data_list(stats: list["LizardData"], header: bool = True) -> list[str]:
        data = [LizardData.csv_header()] if header else []
        data += [stat.to_csv() for stat in stats]
        return data