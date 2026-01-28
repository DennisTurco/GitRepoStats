import yaml
from entities.preferences import (AuthorStatsPreferences, CodeComplexityPreference, CodeDuplicationPreference, CodeOwnershipPreference, Preferences)

PREFERENCE_FILE_PATH = './config/preferences.yaml'

class PreferenceReader:
    @staticmethod
    def read_preferences_from_yaml():
        try:
            with open(PREFERENCE_FILE_PATH) as stream:
                config = yaml.safe_load(stream)

                try:
                    author_stats = config['AuthorStats']
                    code_ownership = config['CodeOwnership']
                    code_duplication = config['CodeDuplication']
                    code_complexity = config['CodeComplexity']
                except KeyError as e:
                    raise KeyError(f"Missing section on file YAML: {e}")

                try:
                    author_stats_pref = AuthorStatsPreferences(
                        author_stats['ExcludeExtensions']
                    )
                    code_ownership_pref = CodeOwnershipPreference(
                        code_ownership['ExcludeExtensions'],
                        code_ownership['ShowZeroPercentAuthorsIfLessThan']
                    )
                    code_duplication_pref = CodeDuplicationPreference(
                        code_duplication['Threshold'],
                        code_duplication['WindowSize'],
                        code_duplication['MaxHammingDiff'],
                        code_duplication['MaxNlocDiff']
                    )
                    code_complexity_pref = CodeComplexityPreference(
                        code_complexity.get('ExcludeExtensions', []), # empty if missing
                        code_complexity.get('ExcludeFunctions', [])
                    )
                except KeyError as e:
                    raise KeyError(f"Missing key in the YAML file: {e}")

                return Preferences(
                    author_stats_pref,
                    code_ownership_pref,
                    code_duplication_pref,
                    CodeComplexity=code_complexity_pref
                )

        except FileNotFoundError:
            raise FileNotFoundError(f"Preference file not found: {PREFERENCE_FILE_PATH}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Parsing YAML error: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred during YAML preference file: {e}")
