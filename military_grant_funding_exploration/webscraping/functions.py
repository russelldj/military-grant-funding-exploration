from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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
