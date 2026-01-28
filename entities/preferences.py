from dataclasses import dataclass

@dataclass
class AuthorStatsPreferences:
    ExcludeExtensions: set[str]

@dataclass
class CodeOwnershipPreference:
    ExcludeExtensions: set[str]
    ShowZeroPercentAuthorsIfLessThan: int

@dataclass
class CodeDuplicationPreference:
    Threshold: float
    WindowSize: int
    MaxHammingDiff: int
    MaxNlocDiff: int

@dataclass
class CodeComplexityPreference:
    ExcludeExtensions: set[str]
    ExcludeFunctions: set[str]

@dataclass
class Preferences():
    AuthorStat: AuthorStatsPreferences
    CodeOwnership: CodeOwnershipPreference
    CodeDuplication: CodeDuplicationPreference
    CodeComplexity: CodeComplexityPreference
