import yaml
from entities.preferences import (CodeComplexityPreference, CodeDuplicationPreference, CodeOwnershipPreference, Preferences)

PREFERENCE_FILE_PATH = './config/preferences.yaml'

class PreferenceReader:
    @staticmethod
    def read_preferences_from_yaml():
        try:
            with open(PREFERENCE_FILE_PATH) as stream:
                config = yaml.safe_load(stream)

                try:
                    code_ownership = config['CodeOwnership']
                    code_duplication = config['CodeDuplication']
                    code_complexity = config['CodeComplexity']
                except KeyError as e:
                    raise KeyError(f"Sezione mancante nel file YAML: {e}")

                try:
                    code_ownership_pref = CodeOwnershipPreference(
                        code_ownership['ExcludeFiles'],
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
