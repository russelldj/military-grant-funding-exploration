from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
import time
import pandas as pd
import os
from military_grant_funding_exploration.constants import DATA_FOLDER
from pathlib import Path

def wait_for_loading():
    loading_pane = WebDriverWait(driver, timeout=2).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='loadingGlassPane']"))
    )
    lp_style = loading_pane.get_attribute("style")
    while 'wait' in lp_style:
        loading_pane = WebDriverWait(driver, timeout=2).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='loadingGlassPane']"))
        )
        lp_style = loading_pane.get_attribute("style")

def open_fmt_menu(short_timeout=1, long_timeout=2):
    # Locate and click open data format menu
    viz_toolbar = WebDriverWait(driver, timeout=timeout).until(
        EC.presence_of_element_located((By.ID, "viz-viewer-toolbar"))
    )
    data_format_button = WebDriverWait(viz_toolbar, timeout=timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, "toolbar-item.collaborate"))
    )
    wait_for_loading()
    data_format_button.click()
    crosstab_button = driver.find_element(By.XPATH, "//*[@data-tb-test-id='download-flyout-download-crosstab-MenuItem']")
    wait_for_loading()
    crosstab_button.click()

def get_crosstab_df(sheet_name):
    # Download a given spreasheet ('crosstab') data view
    sheet_selection = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Single Sheet Selection']"))
    )
    sheet_button = sheet_selection.find_element(By.XPATH, "//div[@title='{}']".format(sheet_name))
    if sheet_button.get_attribute('aria-selected') == "false":
        sheet_button.click()
    download_button = WebDriverWait(driver, timeout=timeout).until(
        EC.presence_of_element_located((By.XPATH, "//button[@data-tb-test-id='export-crosstab-export-Button']"))
    )
    download_button.click()
    time_counter = 0
    sheet_fn = dwnld_fldr+"/{}.xlsx".format(sheet_name)
    while not os.path.exists(sheet_fn):
        time.sleep(1)
        time_counter += 1
        if time_counter > 10:break
    try:
        sheet_df = pd.read_excel(sheet_fn, engine="openpyxl")
    except:
        # Not sure why but rarely a pause is needed here
        time.sleep(5)
        sheet_df = pd.read_excel(sheet_fn, engine="openpyxl")
    return sheet_df

# Constants
driver = webdriver.Firefox()
timeout = 20
dwnld_fldr = "/Users/patrick/Downloads"
num_campuses = 14 #Can only handle as many campuses as fit in the window for now

# Use the driver to render the JavaScript webpage
# Following URL found by rendering this webpage in selenium: https://www.universityofcalifornia.edu/about-us/information-center/sponsors
URL = "https://visualizedata.ucop.edu/t/Public/views/Sponsors/Dashboard"
driver.get(URL)
elem = WebDriverWait(driver, timeout=timeout).until(
    EC.presence_of_element_located((By.XPATH, f"//*[@id='tabZoneId65']"))
)
# Open the fiscal year menu
menu_content = WebDriverWait(elem, timeout=timeout).until(
    EC.presence_of_element_located((By.XPATH, f".//span[@role='combobox']"))
)
menu_content.click()
menu_items = WebDriverWait(menu_content, timeout=timeout).until(
    EC.presence_of_all_elements_located((By.XPATH, '//div[@role="checkbox"]'))
)
# De-select most recent year
checkbox = menu_items[-1].find_element(By.CLASS_NAME, "FICheckRadio")
wait_for_loading()
checkbox.click()
# Loop over all fiscal years
for year_index in range(len(menu_items))[1:]:
    # Find and select a given year
    if year_index > 1:
        menu_content = WebDriverWait(elem, timeout=timeout).until(
            EC.presence_of_element_located((By.XPATH, f".//span[@role='combobox']"))
        )
        wait_for_loading()
        menu_content.click()
        menu_items = WebDriverWait(menu_content, timeout=timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@role="checkbox"]'))
        )
        # De-select previous year
        checkbox = menu_items[year_index-1].find_element(By.CLASS_NAME, "FICheckRadio")
        wait_for_loading()
        checkbox.click()
    wait_for_loading()
    menu_items = WebDriverWait(menu_content, timeout=timeout).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@role="checkbox"]'))
    )
    checkbox = menu_items[year_index].find_element(By.CLASS_NAME, "FICheckRadio")
    checkbox.click()
    fiscal_year = menu_items[year_index].find_element(By.CLASS_NAME, "FIText").get_attribute("title")
    # Click out of fiscal year menu
    clear_glass = driver.find_element(By.CLASS_NAME, "tab-glass.clear-glass.tab-widget")
    wait_for_loading()
    clear_glass.click()

    # Import sheet containing totals per campus
    wait_for_loading()
    open_fmt_menu()
    wait_for_loading()
    campus_df = get_crosstab_df("Campus")
    campus_df.columns.values[0] = "Campus"
    campus_df['Fiscal Year'] = fiscal_year
    if not 'final_campustotal_df' in locals():
        final_campustotal_df = campus_df
    else:
        final_campustotal_df = pd.concat([final_campustotal_df, campus_df], ignore_index=True, axis=0)
    # num_campuses = campus_df.shape[0] #Defined as a constant above for now

    # Locate block of campus labels
    campus_tabzone = WebDriverWait(driver, timeout=timeout).until(
        EC.presence_of_element_located((By.XPATH, f"//*[@id='tabZoneId30']"))
    )
    campus_block = WebDriverWait(campus_tabzone, timeout=timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, "tab-tvYLabel.tvimagesNS"))
    )
    
    # Set spacing for clicking through campuses
    yoffset = campus_block.size['height']/(num_campuses-1)
    h = campus_block.size['height']
    y = campus_block.location['y']
    y_0 = y - (h/2) + (yoffset)/2
    campus_offsets = []
    for i in range(num_campuses):
        y_campus = y_0 + yoffset*i
        campus_offsets.append(y_campus - y)
    y_max = y+h/2
    
    # Loop over all campuses
    for campus_i, offset in enumerate(campus_offsets):
        # Last 1-2 campuses may lie outside window and are not selectable
        # Could try to automate scrolling before selection, but doing so manually didn't help
        if 'campus_names' in locals():
            if campus_i == len(campus_names)-1:
                offset = y_max - y
            elif campus_i > len(campus_names)-1:
                continue
        # Re-locate campus block and select a campus
        campus_tabzone = WebDriverWait(driver, timeout=20).until(
            EC.presence_of_element_located((By.XPATH, f"//*[@id='tabZoneId30']"))
        )
        campus_block = WebDriverWait(campus_tabzone, timeout=5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tab-tvYLabel.tvimagesNS"))
        )
        wait_for_loading()
        ActionChains(driver).move_to_element_with_offset(campus_block, xoffset=0, yoffset=offset).click().perform()
        wait_for_loading()
        time.sleep(3) #idk why this is necessary
        if campus_i == 0:
            campus_tabzone = WebDriverWait(driver, timeout=timeout).until(
                EC.presence_of_element_located((By.XPATH, f"//*[@id='tabZoneId30']"))
            )
            campus_block = WebDriverWait(campus_tabzone, timeout=timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tab-tvYLabel.tvimagesNS"))
            )
            campus_labels = WebDriverWait(campus_block, timeout=timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tab-vizHeaderWrapper']"))
            )
            aria_labels = [cl.get_attribute('aria-label') for cl in campus_labels]
            campus_names = [cl.split(',')[0] for cl in aria_labels if "Location Name" in cl]

        # Download sponsor table
        wait_for_loading()
        open_fmt_menu()
        wait_for_loading()
        sponsor_df = get_crosstab_df("Sponsor Table")

        # Update sponsor table before adding to aggregate dataframe
        sponsor_df.columns.values[0] = "Sponsor Name"
        sponsor_df.columns.values[1] = "Sponsor Location"
        sponsor_df.columns.values[2] = "Sponsor Type"
        sponsor_df['Campus'] = campus_names[campus_i]
        sponsor_df['Fiscal Year'] = fiscal_year
        if not 'final_sponsor_df' in locals():
            final_sponsor_df = sponsor_df
        else:
            final_sponsor_df = pd.concat([final_sponsor_df, sponsor_df], ignore_index=True, axis=0)

        # Remove downloaded sheets before moving to next campus
        os.remove(dwnld_fldr+"/Sponsor Table.xlsx")
    # Delete campus sheet
    os.remove(dwnld_fldr+"/Campus.xlsx")

# Save to csv
outputfn = Path(DATA_FOLDER, "01_initial", "UC_published", 'aggregate_sponsor_tables.csv')
outputfn.parent.mkdir(exist_ok=True, parents=True)
final_sponsor_df.to_csv(outputfn)
outputfn = Path(DATA_FOLDER, "01_initial", "UC_published", 'aggregate_campus_totals.csv')
final_campustotal_df.to_csv(outputfn)

# End session
driver.close()
