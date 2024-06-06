from pathlib import Path

CODE_FOLDER = Path(__file__).parent
DATA_FOLDER = Path(CODE_FOLDER, "..", "data").resolve()
VIS_FOLDER = Path(CODE_FOLDER, "..", "visualizations").resolve()

START_YEAR_KEY = "start_year"
START_MONTH_KEY = "start_month"
START_DAY_KEY = "start_day"

END_YEAR_KEY = "end_year"
END_MONTH_KEY = "end_month"
END_DAY_KEY = "end_day"

FUNDING_AMOUNT_KEY = "funding_amount"

TITLE_KEY = "title"
FUNDER_KEY = "funder"
INVESTIGATOR_KEY = "investigator"
ABSTRACT_KEY = "abstract"
RESULTING_PUBLICATIONS_KEY = "resulting_publications"

FIELDS_OF_RESEACH_KEY = "fields_of_research_key"
UNITS_OF_ASSESSMENT_KEY = "units_of_assessment_key"
HEALTH_CATEGORY_KEY = "health_categories_key"
RESEARCH_ACTIVITY_CODES_KEY = "research_activities_codes_key"
SDG_GOALS_KEY = "SDG_goals_kwy"

TLDR_KEY = "tldr"
TOP_KEYWORDS_KEY = "top_keywords"
KEY_HIGHLIGHTS_KEY = "key_highlights"

HREF_KEY = "href"
