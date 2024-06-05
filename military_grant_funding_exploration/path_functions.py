from pathlib import Path

from military_grant_funding_exploration.constants import DATA_FOLDER


def get_DoD_DTIC_initial_path(campus):
    return Path(DATA_FOLDER, "01_initial", "DoD_DTIC", f"{campus}_dtic_webscraped.json")
