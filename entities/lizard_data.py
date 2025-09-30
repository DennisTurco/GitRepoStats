from enum import Enum


class LizardLocation():
    function: str
    lines: str
    file: str

    # to slice something like: CodeNotFoundException::CodeNotFoundException@37-41@D:\Projects\ISTrust\Casino\ISTrust.Casino\Exceptions\CodeNotFoundException.cs
    # to CodeNotFoundException::CodeNotFoundException, 37-41, D:\Projects\ISTrust\Casino\ISTrust.Casino\Exceptions\CodeNotFoundException.cs
    def __init__(self, location: str):
        end_function = 0
        start_lines = 0
        end_lines = 0
        start_file = 0
        index = 0
        for char in location:
            if char == '@':
                if end_function == 0:
                    end_function = index
                    start_lines = index + 1
                else:
                    end_lines = index - 1
                    start_file = index + 1
            index += 1
        self.function = location[:end_function]
        self.lines = location[start_lines:end_lines]
        self.file = location[start_file:]

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

class LizardData():
    nloc: int # Number of Lines of Code
    ccn: int # Cyclomatic Complexity Number.(complex if > 10)
    token: int # code size metric
    param: int # params number
    length: int # function row length (similar to nloc but including declarations, exc...)
    location: LizardLocation # location function
    status: Status

    def __init__(self, nloc: int, ccn: int, token: int, param: int, length: int, location: str):
        self.nloc = nloc
        self.ccn = ccn
        self.token = token
        self.param = param
        self.length = length
        self.location = LizardLocation(location)

        if nloc <= 30 and ccn <= 10 and token <= 100 and param <= 4:
            self.status = Status.HEALTHY
        elif nloc <= 100 and ccn <= 20 and token <= 500 and param <= 7:
            self.status = Status.NEEDS_ATTENTION
        else:
            self.status = Status.AT_RISK

    def __str__(self) -> str:
        return f"nloc: {self.nloc}, ccn: {self.ccn}, token: {self.token}, param: {self.param}, length: {self.length}, location: {self.location.file}, status: {self.status}"

    def to_csv(self) -> str:
        return f"{self.status.to_emoji()},{self.nloc},{self.ccn},{self.token},{self.param},{self.length},{self.location.function},{self.location.lines},{self.location.file}"

    @staticmethod
    def csv_header() -> str:
        return "Status,NLOC,CCN,Token,Param,Length,Function,Lines,File"

    @staticmethod
    def to_csv_data_list(stats: list["LizardData"], header: bool = True) -> list[str]:
        data = [LizardData.csv_header()] if header else []
        data += [stat.to_csv() for stat in stats]
        return data