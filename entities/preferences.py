from dataclasses import dataclass

@dataclass
class CodeOwnershipPreference:
    ExcludeFiles: list[str]
    ShowZeroPercentAuthorsIfLessThan: int

@dataclass
class CodeDuplicationPreference:
    Threshold: float
    WindowSize: int
    MaxHammingDiff: int
    MaxNlocDiff: int

@dataclass
class CodeComplexityPreference:
    ExcludeExtensions: list[str]
    ExcludeFunctions: list[str]

@dataclass
class Preferences():
    CodeOwnership: CodeOwnershipPreference
    CodeDuplication: CodeDuplicationPreference
    CodeComplexity: CodeComplexityPreference
