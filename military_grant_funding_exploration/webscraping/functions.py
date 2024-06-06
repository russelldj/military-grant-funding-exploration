from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import calendar

MONTH_STR_TO_INT_DICT = {s: i + 1 for i, s in enumerate(list(calendar.month_abbr)[1:])}
MONTH_STR_TO_INT_DICT.update(
    {s: i + 1 for i, s in enumerate(list(calendar.month_name)[1:])}
)


# https://stackoverflow.com/questions/41043582/how-to-wait-for-presence-of-an-element-with-non-empty-content
class WaitForNonEmptyText:
    def __init__(self, by, locator):
        self.by = by
        self.locator = locator

    def __call__(self, driver):
        try:
            element_text = driver.find_element(self.by, self.locator).text.strip()
            return element_text != ""
        except StaleElementReferenceException:
            return False


def month_to_number(month_str):
    if isinstance(month_str, int):
        return month_str
    return MONTH_STR_TO_INT_DICT[month_str]


def parse_int_from_str(string):
    digits_str = "".join([c for c in string if c.isdigit()])

    return int(digits_str) if len(digits_str) > 0 else None


def drop_none_values(input_dict):
    return {k: v for (k, v) in input_dict.items() if (v is not None)}
