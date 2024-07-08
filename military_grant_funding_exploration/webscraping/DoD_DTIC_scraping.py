import json
from pathlib import Path
import argparse
from tqdm import tqdm

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from military_grant_funding_exploration.webscraping.functions import (
    WaitForNonEmptyText,
    parse_int_from_str,
    month_to_number,
    drop_none_values,
)
from military_grant_funding_exploration.path_functions import get_DoD_DTIC_initial_path
from military_grant_funding_exploration.constants import (
    START_YEAR_KEY,
    START_MONTH_KEY,
    START_DAY_KEY,
    END_YEAR_KEY,
    END_DAY_KEY,
    END_MONTH_KEY,
    FUNDING_AMOUNT_KEY,
    RESULTING_PUBLICATIONS_KEY,
    TITLE_KEY,
    FUNDER_KEY,
    INVESTIGATOR_KEY,
    ABSTRACT_KEY,
    HREF_KEY,
    TLDR_KEY,
    TOP_KEYWORDS_KEY,
    KEY_HIGHLIGHTS_KEY,
    FIELDS_OF_RESEACH_KEY,
    UNITS_OF_ASSESSMENT_KEY,
    HEALTH_CATEGORY_KEY,
    RESEARCH_ACTIVITY_CODES_KEY,
    SDG_GOALS_KEY,
    GRANT_NUMBER_KEY,
)


CAMPUS_URL_DICT = {
    "ucsd": "https://dtic.dimensions.ai/discover/grant?search_mode=content&or_facet_research_org=grid.266100.3&order=funding",
    "ucla": "https://dtic.dimensions.ai/discover/grant?search_mode=content&or_facet_research_org=grid.19006.3e&order=funding",
    "ucberkeley": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.47840.3f",
    "ucdavis": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.27860.3b",
    "ucirvine": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.266093.8",
    "ucr": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.266097.c",
    "ucsb": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.133342.4",
    "ucsf": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.266102.1",
    "ucsc": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.205975.c",
    "ucmerced": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.266096.d",
    "lawrence_berekeley": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.184769.5",
    "lawrence_livermore": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.250008.f",
    "los_alamos": "https://dtic.dimensions.ai/discover/grant?search_mode=content&order=funding&or_facet_research_org=grid.148313.c",
}


def get_summary_text(browser, element_name, timeout=200, split=False):
    try:
        WebDriverWait(browser, timeout=timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//button[@id='tab_{element_name}']")
            )
        ).click()
        # Get the corresponding text
        WebDriverWait(browser, timeout=timeout).until(
            WaitForNonEmptyText(
                By.XPATH, f"//div[@aria-labelledby='tab_{element_name}']"
            )
        )
        text_div = WebDriverWait(browser, timeout=timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[@aria-labelledby='tab_{element_name}']")
            )
        )
    except TimeoutException:
        return None

    text = text_div.text

    if split:
        return text.splitlines()
    return text


def index_maybe_in_list(list_of_elements, search_elem):
    return (
        list_of_elements.index(search_elem) if search_elem in list_of_elements else None
    )


def parse_research_categories(research_categories_text):
    split = research_categories_text.splitlines()

    # These headers may or may not be present in the split text
    potential_headers = (
        "Fields of Research (ANZSRC 2020)",
        "Units of Assessment",
        "Health Category (HRCS)",
        "Research Activity Codes (HRCS)",
        "Sustainable Development Goals",
    )
    # These are the corresponding fields for each header
    category_keys = (
        FIELDS_OF_RESEACH_KEY,
        UNITS_OF_ASSESSMENT_KEY,
        HEALTH_CATEGORY_KEY,
        RESEARCH_ACTIVITY_CODES_KEY,
        SDG_GOALS_KEY,
    )
    # This is either a integer ID for the index at which the value occurs or None if not present
    potential_header_inds = [
        index_maybe_in_list(split, header) for header in potential_headers
    ]
    # Pair the header inds and the associated category for each one that is present
    non_null_header_cat_pairs = [
        hc for hc in zip(potential_header_inds, category_keys) if hc[0] is not None
    ]
    # If none of the requested headers are present, return an empty dict
    if len(non_null_header_cat_pairs) == 0:
        return {}

    # Change from a list of tuples to two lists
    present_header_inds, present_category_keys = zip(*non_null_header_cat_pairs)
    # Append None so the last slice parses all the way to the end
    present_header_inds = present_header_inds + (None,)
    # Turn the split data into a dictionary. The key is the category and the value is the data from
    # the start ind + 1 (so the header isn't included) to the next ind. Since the last ind
    # is set to None, the last slice will go all the way to the end
    data_dict = {
        present_category_keys[i]: split[
            present_header_inds[i] + 1 : present_header_inds[i + 1]
        ]
        for i in range(len(present_category_keys))
    }

    return data_dict


def parse_section_details(section_details_text):
    split = section_details_text.splitlines()

    data_dict = {}
    data_dict[FUNDING_AMOUNT_KEY] = parse_int_from_str(split[1])
    # TODO see if replacing this with ("Funding period" in split) is more robust
    if len(split) > 4:
        data_dict[START_YEAR_KEY] = parse_int_from_str(split[3])
        data_dict[START_MONTH_KEY] = month_to_number(split[4].split(" ")[1])
        data_dict[START_DAY_KEY] = parse_int_from_str(split[4])

    if "-" in split:
        if len(split) > 6:
            data_dict[END_YEAR_KEY] = parse_int_from_str(split[6])
        if len(split) > 7:
            data_dict[END_MONTH_KEY] = month_to_number(split[7].split(" ")[1])
            data_dict[END_DAY_KEY] = parse_int_from_str(split[7])

    if "Resulting DOD publications" in split:
        pubs_ind = split.index("Resulting DOD publications")
        # Take the next field after that text
        data_dict[RESULTING_PUBLICATIONS_KEY] = parse_int_from_str(split[pubs_ind + 1])

    data_dict = drop_none_values(data_dict)

    return data_dict


def get_heading_info(browser, return_title=False, return_funder=False):
    # Get the title element
    title_elem = browser.find_elements(By.XPATH, "//h1[@data-bt='details-title']")
    # The should only be one element matching this, if not we have an issue
    assert len(title_elem) == 1

    # Get the parent of the title. Unfortunately we can't search for it directly
    title_pane_elem = title_elem[0].find_element(By.XPATH, "./..")
    text_pane_text_split = title_pane_elem.text.split("\n")

    parsed_dict = {}

    # Parse the title if requested
    if return_title:
        parsed_dict[TITLE_KEY] = text_pane_text_split[1]
    # Parse the funder if requested
    if return_funder:
        parsed_dict[FUNDER_KEY] = text_pane_text_split[2][8:]

    # Parse the grant number
    grant_number_str = text_pane_text_split[-1]
    parsed_dict[GRANT_NUMBER_KEY] = grant_number_str.split(" ")[-1]

    return parsed_dict


def scrape_and_save(
    url,
    output_filename,
    scroll_to_bottom=True,
    parse_per_grant_pages: bool = True,
    timeout=200,
    wait_for_scroll=2,
):
    # establish connection
    browser = webdriver.Firefox()
    browser.get(url)

    # wait for the element with the ID of wrapper
    WebDriverWait(browser, timeout=timeout).until(
        EC.presence_of_element_located(
            (By.XPATH, "//article[@data-bt='project_result_item']")
        )
    )

    # Scroll to the bottom to show all elements
    # Only done if requested
    while scroll_to_bottom:
        # scroll down to bottom of current view
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # wait until loading-spinner comes into view (i.e., hit the bottom of current view)
        try:
            WebDriverWait(browser, wait_for_scroll).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-testid='loading-spinner']")
                )
            )
        except TimeoutException:
            print("hit the bottom of the inifinite scroll")
            break

    # click all the "more" buttons to reveal the full abstract
    buttons_more = browser.find_elements(By.XPATH, '//button[text()="more"]')
    for button in tqdm(buttons_more, desc='Clicking "more" buttons to show abstract'):
        button.click()

    # retrieve text from each article element
    elems_grants = browser.find_elements(
        By.XPATH, "//article[@data-bt='project_result_item']"
    )

    # parse each article by title, funding org, principal investigator, abstract, funding value, start year, end year

    all_grants = []

    for elem_grant in tqdm(
        elems_grants, desc="Parsing basic information from each grant"
    ):
        # Get more detailed information by clicking on the specific grant
        detail_link = elem_grant.find_element(By.XPATH, ".//*[@data-bt='detail_link']")
        href = detail_link.get_attribute("href")

        # Parse the data that's available from the preview on the main list
        article_text_split = elem_grant.text.split("\n")

        # Remove leading "to "
        investigator = article_text_split[2][3:]
        funding_amount = parse_int_from_str(article_text_split[4])

        # Some of this data may be overwritten later, but it's faster to parse here, so both methods
        # are kept in case only the minimal set is requested

        # Include all the fields that are always there
        grant_data = {
            TITLE_KEY: article_text_split[0],
            FUNDER_KEY: article_text_split[1],
            INVESTIGATOR_KEY: investigator,
            ABSTRACT_KEY: article_text_split[3],
            FUNDING_AMOUNT_KEY: funding_amount,
            HREF_KEY: href,
        }
        # Include optional fields
        if len(article_text_split) > 5:
            grant_data[START_YEAR_KEY] = parse_int_from_str(article_text_split[5])
        if len(article_text_split) > 8:
            grant_data[END_YEAR_KEY] = parse_int_from_str(article_text_split[7])

        grant_data = drop_none_values(grant_data)

        # Add the information from this grant to the list of all grants
        all_grants.append(grant_data)

    # Get additional information that can be much slower to parse
    if parse_per_grant_pages:
        for grant_data in tqdm(
            all_grants,
            desc="Parsing addtional information by visiting each grant-specific page",
        ):
            # Go to the page for that grant
            browser.get(grant_data[HREF_KEY])

            # Parse the AI summary text
            grant_data[TLDR_KEY] = get_summary_text(
                browser=browser, element_name="tldr"
            )
            grant_data[KEY_HIGHLIGHTS_KEY] = get_summary_text(
                browser=browser, element_name="key-highlights", split=True
            )
            grant_data[TOP_KEYWORDS_KEY] = get_summary_text(
                browser=browser, element_name="top-keywords", split=True
            )

            try:
                # TODO Parse the research categories
                research_cat_sec = WebDriverWait(browser, timeout=timeout).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//section[@data-bt='aside_section_research_categories']",
                        )
                    )
                )
                grant_data.update(parse_research_categories(research_cat_sec.text))
            except TimeoutException:
                pass

            # Parse the funding amount and years
            section_details = WebDriverWait(browser, timeout=timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-bt='aside_section_content']")
                )
            )
            # Add the section details data
            grant_data.update(parse_section_details(section_details.text))
            # Add the header data
            grant_data.update(get_heading_info(browser=browser))

    # Close the browser session
    browser.close()

    all_grants_dfs = []
    for i, grant_data in enumerate(all_grants):
        # If the field is a list, transform it into a one-length tuple so there's not a
        # length mismatch
        sanitized_grant_data = {
            k: ((v,) if isinstance(v, list) else v) for k, v in grant_data.items()
        }
        # Convert the data to a data frame
        grant_df = pd.DataFrame(sanitized_grant_data, index=[i])
        all_grants_dfs.append(grant_df)

    # Transform the data into a single pandas dataframe
    all_grants_dfs = pd.concat(all_grants_dfs)

    # Ensure there's a folder to save the data
    output_filename.parent.mkdir(exist_ok=True, parents=True)
    # save dataframe to csv file
    all_grants_dfs.to_json(output_filename, orient="index", indent=4)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--campuses",
        nargs="+",
        default=list(CAMPUS_URL_DICT.keys()),
        help="Which campuses to scrape data from. Provide as many options as you want from the "
        + f"following list: {list(CAMPUS_URL_DICT.keys())}",
    )
    parser.add_argument(
        "--only-scrape-subset",
        action="store_true",
        help="Only parse a subset of grants, specifically only those visible without scrolling down. "
        + "Useful for initial testing",
    )
    parser.add_argument(
        "--only-scrape-basic-info",
        action="store_true",
        help="Only parse the data from the summary view, which is much faster than opening each grant's page",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    for campus in args.campuses:
        print(f"Parsing data from {campus}")
        url = CAMPUS_URL_DICT[campus]
        output_filename = get_DoD_DTIC_initial_path(campus)
        scrape_and_save(
            url=url,
            output_filename=output_filename,
            scroll_to_bottom=not args.only_scrape_subset,
            parse_per_grant_pages=not args.only_scrape_basic_info,
        )
