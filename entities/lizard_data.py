import difflib
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import cast

from simhash import Simhash


@dataclass
class LizardLocation:
    function: str
    lines: str
    file: str


class Status(Enum):
    HEALTHY = 1
    NEEDS_ATTENTION = 2
    AT_RISK = 3

    def to_emoji(self) -> str:
        return {Status.HEALTHY: "✅", Status.NEEDS_ATTENTION: "⚠️", Status.AT_RISK: "❌"}[self]



nloc_healthy_limit = 30
nloc_warning_limit = 100
ccn_healthy_limit = 10
ccn_warning_limit = 20
token_healthy_limit = 100
token_warning_limit = 500
param_healthy_limit = 4
param_warning_limit = 7

@dataclass
class LizardData:
    nloc: int  # Number of Lines of Code
    ccn: int  # Cyclomatic Complexity Number.(complex if > 10)
    token: int  # code size metric
    param: int  # params number
    length: int  # function row length (similar to nloc but including declarations, exc...)
    code: str
    location: LizardLocation  # location function
    status: Status = field(init=False)
    hash_value: int = field(init=False, repr=False)


    def __post_init__(self):
        if (self.nloc <= nloc_healthy_limit and self.ccn <= ccn_healthy_limit
            and self.token <= token_healthy_limit and self.param <= param_healthy_limit):
            self.status = Status.HEALTHY
        elif (self.nloc <= nloc_warning_limit and self.ccn <= ccn_warning_limit
            and self.token <= token_warning_limit and self.param <= param_warning_limit):
            self.status = Status.NEEDS_ATTENTION
        else:
            self.status = Status.AT_RISK

        self.hash_value = int(cast(int, Simhash(self.code.split()).value))

    # to obtain a propotional score based on data importance
    def similarity_score(self, other: "LizardData") -> float:
        diff_nloc = abs(self.nloc - other.nloc)
        diff_ccn = abs(self.ccn - other.ccn)
        diff_token = abs(self.token - other.token)
        diff_param = abs(self.param - other.param)
        diff_length = abs(self.length - other.length)

        # this because token and lenght are more important than param for this check
        numeric_score = (
            0.3 * diff_nloc
            + 0.3 * diff_token
            + 0.2 * diff_ccn
            + 0.1 * diff_param
            + 0.1 * diff_length
        )

        text_similarity = difflib.SequenceMatcher(None, self.code, other.code).ratio()
        text_score = (1 - text_similarity) * 100  # 0 = same, 100 = completly diference

        score = 0.6 * numeric_score + 0.4 * text_score
        return score

    def to_csv(self) -> str:
        return f"""{self.status.to_emoji()}|{self.nloc}|{self.ccn}|{self.token}|{self.param}|
            {self.length}|{self.location.function}|{self.location.lines}|{self.location.file}"""

    @staticmethod
    def csv_header_summary() -> str:
        return "Status|Category|ValueAvg"

    @staticmethod
    def csv_header() -> str:
        return "Status|NLOC|CCN|Token|Param|Length|Function|Lines|File"

    @staticmethod
    def to_csv_data_list_summary(stats: list["LizardData"], header: bool = True) -> list[str]:
        data = [LizardData.csv_header_summary()] if header else []

        complexity_grouped: defaultdict[str, int] = defaultdict(int)
        for stat in stats:
            complexity_grouped["nloc"] += stat.nloc
            complexity_grouped["ccn"] += stat.ccn
            complexity_grouped["token"] += stat.token
            complexity_grouped["param"] += stat.param

        total_elem = len(stats)
        for cg_key, cg_value in complexity_grouped.items():
            avg_value = cg_value / total_elem
            status = LizardData.__get_status_based_on_type(cg_key, int(avg_value))
            data.append(f"{status.to_emoji()}|{cg_key}|{avg_value:.2f}")

        return data

    @staticmethod
    def to_csv_data_list(stats: list["LizardData"], header: bool = True) -> list[str]:
        data = [LizardData.csv_header()] if header else []
        data += [stat.to_csv() for stat in stats]
        return data

    @staticmethod
    def __get_status_based_on_type(type: str, value: int) -> Status:
        healthy_limit = 0
        warning_limit = 0
        match type:
            case "nloc":
                healthy_limit = nloc_healthy_limit
                warning_limit = nloc_warning_limit
            case "ccn":
                healthy_limit = ccn_healthy_limit
                warning_limit = ccn_warning_limit
            case "token":
                healthy_limit = token_healthy_limit
                warning_limit = token_warning_limit
            case "param":
                healthy_limit = param_healthy_limit
                warning_limit = param_warning_limit
            case _:
                raise ValueError(f"type '{type}' is not valid")
        return LizardData.__get_status_by_values(value, healthy_limit, warning_limit)

    @staticmethod
    def __get_status_by_values(value: int, healthy_limit: int, warning_limit: int):
        if value <= healthy_limit:
            return Status.HEALTHY
        if value <= warning_limit:
            return Status.NEEDS_ATTENTION
        return Status.AT_RISK