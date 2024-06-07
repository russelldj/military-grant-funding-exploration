from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


options = Options()
options.add_argument("--headless")
# driver = webdriver.Firefox(options=options)
driver = webdriver.Firefox()

# Now we use the driver to render the JavaScript webpage.
URL = "https://visualizedata.ucop.edu/t/Public/views/AwardExplorerPublic_15958737997250/Projects?:embed=y&amp;:showVizHome=no&amp;:host_url=https%3A%2F%2Fvisualizedata.ucop.edu%2F&amp;:embed_code_version=3&amp;:tabs=no&amp;:toolbar=yes&amp;:showAppBanner=false&amp;:display_spinner=no&amp;:loadOrderID=0"
driver.get(URL)
elem = WebDriverWait(driver, timeout=20).until(
    EC.presence_of_element_located((By.XPATH, f"//div[@id='tabZoneId107']"))
)
menu_content = WebDriverWait(elem, timeout=20).until(
    EC.presence_of_element_located(
        (By.XPATH, f".//span[@aria-label='Project type (All)']")
    )
)
menu_content.click()
menu_items = driver.find_elements(By.XPATH, '//div[@role="menuitem"]')
second_item = menu_items[1]
second_item.click()
breakpoint()
