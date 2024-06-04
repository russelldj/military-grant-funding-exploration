from pathlib import Path

CODE_FOLDER = Path(__file__).parent
DATA_FOLDER = Path(CODE_FOLDER, "..", "data").resolve()

START_YEAR_KEY = "start_year"
START_MONTH_KEY = "start_month"
START_DAY_KEY = "start_day"

END_YEAR_KEY = "end_year"
END_MONTH_KEY = "end_month"
END_DAY_KEY = "end_day"

FUNDING_AMOUNT_KEY = "funding_amount"

RESULTING_PUBLICATIONS_KEY = "resulting_publications"
