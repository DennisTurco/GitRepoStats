from dataclasses import dataclass
from entities.lizard_data import LizardData

@dataclass
class DuplicationData:
    func_a: LizardData
    func_b: LizardData
    similarity_score: float

    def to_csv(self) -> str:
        return f"{self.similarity_score:.2f}|{self.func_a.location.file}|{self.func_a.location.function}|{self.func_b.location.file}|{self.func_b.location.function}"

    @staticmethod
    def csv_header() -> str:
        return "SimilarityScore|FileA|FunctionA|FileB|FunctionB"

    @staticmethod
    def to_csv_data_list(stats: list["DuplicationData"], header: bool = True) -> list[str]:
        data = [DuplicationData.csv_header()] if header else []
        data += [stat.to_csv() for stat in stats]
        return data
