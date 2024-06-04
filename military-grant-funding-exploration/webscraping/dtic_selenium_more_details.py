from pathlib import Path
import json

# todo: got to handle the articles (at the bottom) with missing fields

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd

from functions import WaitForNonEmptyText


def get_summary_text(browser, element_name, timeout=30):
    WebDriverWait(browser, timeout=timeout).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//button[@id='tab_{element_name}']")
        )
    ).click()
    # Get the corresponding text
    WebDriverWait(browser, timeout=timeout).until(
        WaitForNonEmptyText(By.XPATH, f"//div[@aria-labelledby='tab_{element_name}']")
    )
    text_div = WebDriverWait(browser, timeout=timeout).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//div[@aria-labelledby='tab_{element_name}']")
        )
    )
    text = text_div.text
    return text


def index_maybe_in_list(list_of_elements, search_elem):
    return (
        list_of_elements.index(search_elem) if search_elem in list_of_elements else None
    )


def parse_research_categories(research_categories_text):
    split = research_categories_text.splitlines()
    # fields_of_research_ind = min(
    #    [i for i in range(len(split)) if "Fields of Research" in split[i]]
    # )
    research_cat_ind = split.index("Fields of Research (ANZSRC 2020)")
    units_of_assessment_ind = index_maybe_in_list(split, "Units of Assessment")
    # This may not be there
    SDG_goals_ind = index_maybe_in_list(split, "Sustainable Development Goals")

    ret_dict = {}
    ret_dict["research_categories"] = split[
        research_cat_ind + 1 : units_of_assessment_ind
    ]
    # Note that the SDG_goals may be None, but this slice should still work

    if units_of_assessment_ind is not None:
        ret_dict["units_of_assessment"] = split[
            units_of_assessment_ind + 1 : SDG_goals_ind
        ]
    if SDG_goals_ind is not None:
        ret_dict["SDG_goals"] = split[SDG_goals_ind + 1 :]
    return ret_dict


def parse_section_details(section_details_text):
    split = section_details_text.splitlines()
    breakpoint()


def scrape_and_save(url, output_filename, scroll_to_bottom=True):
    # establish connection
    browser = webdriver.Firefox()
    browser.get(url)

    # wait for the element with the ID of wrapper
    try:
        wrapper = WebDriverWait(browser, 8).until(
            EC.presence_of_element_located(
                (By.XPATH, "//article[@data-bt='project_result_item']")
            )
        )
        print("element is present in the DOM now")
    except TimeoutException:
        print("element did not show up")

    # implement infinite scrolling to hit the bottom entry
    while scroll_to_bottom:
        # scroll down to bottom of current view
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # wait until loading-spinner comes into view (i.e., hit the bottom of current view)
        try:
            WAIT_FOR_SCROLL_TIME = 2
            wrapper = WebDriverWait(browser, WAIT_FOR_SCROLL_TIME).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-testid='loading-spinner']")
                )
            )
        except TimeoutException:
            print(
                "hit the bottom of the inifinite scroll"
            )  # if it hits the end of infinite scroll
            break

    # click all the "more" buttons to reveal the full abstract
    buttons_more = browser.find_elements(By.XPATH, '//button[text()="more"]')
    print("clicking all the more button to reveal abstract")
    for button in buttons_more:
        button.click()

    # retrieve text from each article element
    elems_article = browser.find_elements(
        By.XPATH, "//article[@data-bt='project_result_item']"
    )

    # parse each article by title, funding org, principal investigator, abstract, funding value, start year, end year

    articles_data = []

    for elem_article in elems_article:
        # Get more detailed information by clicking on the specific grant
        detail_link = elem_article.find_element(
            By.XPATH, ".//*[@data-bt='detail_link']"
        )
        href = detail_link.get_attribute("href")

        # Parse the data that's available from the abstract
        article_text = elem_article.text
        article_text_split = article_text.split("\n")

        article_data = {
            "title": article_text_split[0],
            "funder": article_text_split[1],
            "investigator": article_text_split[2],
            "abstract": article_text_split[3],
            "funding_amount_usd": article_text_split[4],
            "href": href,
        }
        if len(article_text_split) > 5:
            article_data["start_year"] = article_text_split[5]
        if len(article_text_split) > 8:
            article_data["end_year"] = article_text_split[7]

        articles_data.append(article_data)

    for article_data in articles_data:
        url = article_data["href"]
        browser.get(url)
        # Parse the funding amount and years
        section_details = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@data-bt='aside_section_content']")
            )
        )
        section_details_text = section_details.text

        # Parse the AI summary text
        tldr = get_summary_text(browser=browser, element_name="tldr")
        key_highlights = get_summary_text(
            browser=browser, element_name="key-highlights"
        ).splitlines()
        top_keywords = get_summary_text(
            browser=browser, element_name="top-keywords"
        ).splitlines()
        # TODO Parse the research categories
        research_cat_sec = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//section[@data-bt='aside_section_research_categories']")
            )
        )
        research_cat_text = research_cat_sec.text
        research_cat_dict = parse_research_categories(research_cat_text)
        article_data.update(research_cat_dict)

        article_data["section_details"] = section_details_text
        article_data["tldr"] = tldr
        article_data["top_keywords"] = top_keywords
        article_data["key_highlights"] = key_highlights

    # Ensure there's a folder to save the data
    output_filename.parent.mkdir(exist_ok=True, parents=True)
    # save dataframe to csv file
    with open(output_filename, "w") as outfile_h:
        outfile_h.write(json.dumps(articles_data, indent=4, sort_keys=True))


SCROLL_TO_BOTTOM = False
# Specify which campus, from the list of options below

URL_DICT = {
    "ucsd": "https://dtic.dimensions.ai/discover/grant?search_mode=content&or_facet_research_org=grid.266100.3&not_facet_funder=grid.496791.4&order=funding",
    "ucla": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.19006.3e",
    "ucberkeley": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.47840.3f",
    "ucdavis": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.27860.3b",
    "ucirvine": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.266093.8",
    "ucr": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.266097.c",
    "ucsb": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.133342.4",
    "ucsf": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.266102.1",
    "ucsc": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.205975.c",
    "ucmerced": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.266096.d",
    "lawrence_berekeley": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.184769.5",
    "lawrence_livermore": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.250008.f",
    "los_alamos": "https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.148313.c",
}
# Determine where to save the data, relative to the current file location
DATA_FOLDER = Path(Path(__file__).parent, "..", "..", "data").resolve()

for campus in list(URL_DICT.keys()):
    print(f"Parsing data from {campus}")
    url = URL_DICT[campus]
    output_filename = Path(
        DATA_FOLDER, "DoD", "01_scraped", f"{campus}_dtic_webscraped.json"
    )
    scrape_and_save(url=url, output_filename=output_filename, scroll_to_bottom=True)
