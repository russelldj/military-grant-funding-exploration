# todo: got to handle the articles (at the bottom) with missing fields

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd

## specify url (comment out the line that you don't need)
# filtered by ucsd:
url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&or_facet_research_org=grid.266100.3&not_facet_funder=grid.496791.4&order=funding'
output_filename = 'ucsd_dtic_webscraped.csv'
# # filtered by ucla:
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.19006.3e'
# output_filename = 'ucla_dtic_webscraped.csv'
# # uc berkeley
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.47840.3f'
# output_filename = 'ucberkeley_dtic_webscraped.csv'

# uc davis
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.27860.3b'
# output_filename = 'ucdavis_dtic_webscraped.csv'
# # uc irvine
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.266093.8'
# output_filename = 'ucirvine_dtic_webscraped.csv'
# # uc riverside
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.266097.c'
# output_filename = 'ucr_dtic_webscraped.csv'
# # # uc santa barbara
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.133342.4'
# output_filename = 'ucsb_dtic_webscraped.csv'
# # uc san francisco
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.266102.1'
# output_filename = 'ucsf_dtic_webscraped.csv'

# # uc santa cruz
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.205975.c'
# output_filename = 'ucsc_dtic_webscraped.csv'
# # uc merced
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.266096.d'
# output_filename = 'ucmerced_dtic_webscraped.csv'
# # lawrence berkeley national laboratory (doe)
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.184769.5'
# output_filename = 'lawrence_berkeley_dtic_webscraped.csv'
# # lawrence livermore national laboratory (doe)
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.250008.f'
# output_filename = 'lawrence_livermore_dtic_webscraped.csv'
# los alamos national laboratory (doe)
# url = 'https://dtic.dimensions.ai/discover/grant?search_mode=content&not_facet_funder=grid.496791.4&order=funding&or_facet_research_org=grid.148313.c'
# output_filename = 'los_alamos_dtic_webscraped.csv'

# establish connection
browser = webdriver.Firefox()
browser.get(url)

# wait for the element with the ID of wrapper
try: 
    wrapper = WebDriverWait(browser, 8).until(
        EC.presence_of_element_located((By.XPATH, "//article[@data-bt='project_result_item']"))
    )
    print("element is present in the DOM now")
except TimeoutException:
    print("element did not show up")

# implement infinite scrolling to hit the bottom entry
while True:
    # scroll down to bottom of current view
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # wait until loading-spinner comes into view (i.e., hit the bottom of current view)
    try:
        WAIT_FOR_SCROLL_TIME = 2
        wrapper = WebDriverWait(browser, WAIT_FOR_SCROLL_TIME).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='loading-spinner']"))
        )
    except TimeoutException:
        print("hit the bottom of the inifinite scroll")    #if it hits the end of infinite scroll
        break

# click all the "more" buttons to reveal the full abstract
buttons_more = browser.find_elements(By.XPATH, '//button[text()="more"]')
print('clicking all the more button to reveal abstract')
for button in buttons_more:
    button.click()


# retrieve text from each article element
elems_article = browser.find_elements(By.XPATH, "//article[@data-bt='project_result_item']")

# parse each article by title, funding org, principal investigator, abstract, funding value, start year, end year
final_df = pd.DataFrame(columns=['title'])
for elem_article in elems_article:
    article_text = elem_article.text
    article_text_split = article_text.split('\n')
    if len(article_text_split) == 9:
        article_data = {'title': article_text_split[0], 'funder': article_text_split[1], 'investigator': article_text_split[2], 'abstract': article_text_split[3], 'funding_amount_usd': article_text_split[4], 'start_year': article_text_split[5], 'end_year': article_text_split[7]}
    elif len(article_text_split) < 9:
        # handle when the end date is missing
        try:
            article_data = {'title': article_text_split[0], 'funder': article_text_split[1], 'investigator': article_text_split[2], 'abstract': article_text_split[3], 'funding_amount_usd': article_text_split[4], 'start_year': article_text_split[5]}
        except IndexError:
            article_data = {'title': article_text_split[0], 'funder': article_text_split[1], 'investigator': article_text_split[2], 'abstract': article_text_split[3], 'funding_amount_usd': article_text_split[4]}
    df = pd.DataFrame(data = article_data, index=[0])
    final_df = pd.concat([final_df,df])

# save dataframe to csv file
final_df.to_csv(output_filename)
print('file saved')


