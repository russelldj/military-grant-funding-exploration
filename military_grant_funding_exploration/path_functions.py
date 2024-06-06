from pathlib import Path

from military_grant_funding_exploration.constants import DATA_FOLDER

DOD_DTIC_MERGED_ALL_CAMPUSES_PATH = Path(
    DATA_FOLDER, "02_derived_fields", "DoD_DTIC", "merged_all_campuses.json"
)


def get_DoD_DTIC_initial_path(campus):
    return Path(DATA_FOLDER, "01_initial", "DoD_DTIC", f"{campus}_dtic_webscraped.json")
