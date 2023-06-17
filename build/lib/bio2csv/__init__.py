from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import random

def fetch_paper_details(paper_url, session):
    try:
        paper_res = session.get(paper_url)
        paper_soup = BeautifulSoup(paper_res.text, 'html.parser')
        abstract = paper_soup.find('div', {'class': 'abstract'}).find('p').text
    except AttributeError:
        abstract = "Not found"
    except Exception as e:
        print(f"Error when trying to fetch abstract: {e}")
        abstract = "Not found"
    
    try:
        full_text_res = session.get(paper_url + '.full')
        full_text_soup = BeautifulSoup(full_text_res.text, 'html.parser')
        full_text = full_text_soup.find('div', {'class': 'article fulltext-view'}).text
    except Exception as e:
        print(f"Error when trying to fetch full text: {e}")
        full_text = "Not found"

    return abstract, full_text

def scrape_biorxiv(base_url="https://www.biorxiv.org/collection/genetics?page=", pages=802, get_abstract=True, get_full_text=True):
    # Initialize the session
    session = requests.Session()

    data = []  # Use a list to store the data

    # Loop over all pages
    for i in tqdm(range(pages), desc="Pages", position = 0, leave = True): # Adjust range based on the actual number of pages.
        try:
            url = base_url + str(i)
            res = session.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Get all papers on page
            if 'search' in base_url:
              paper_class = 'highwire-cite highwire-cite-highwire-article highwire-citation-biorxiv-article-pap-list clearfix'
            else:
              paper_class = 'highwire-cite highwire-cite-highwire-article highwire-citation-biorxiv-article-pap-list-overline clearfix'
            papers = soup.find_all('div', {'class': paper_class})
            for paper in tqdm(papers, desc="Papers on page "+str(i), leave=True, position = 1):
                try:
                    title = paper.find('span', {'class': 'highwire-cite-title'}).find('a').text.strip()
                    authors = paper.find('span', {'class': 'highwire-citation-authors'}).text.strip()
                    link = "https://www.biorxiv.org" + paper.find('span', {'class': 'highwire-cite-title'}).find('a')['href']

                    abstract, full_text = None, None
                    if get_abstract or get_full_text:
                        abstract, full_text = fetch_paper_details(link, session)

                    # Append the data to the list
                    paper_data = {"Title": title, "Authors": authors, "Link": link}
                    if get_abstract:
                        paper_data["Abstract"] = abstract
                    if get_full_text:
                        paper_data["Full Text"] = full_text

                    data.append(paper_data)
                except Exception as e:
                    print(f"Error when processing paper: {e}")
                    continue

            # Prevent overloading the server with requests
            time.sleep(random.uniform(0.5, 1.5))  # Adjust the delay as needed
        except Exception as e:
            print(f"Error on page {i}: {e}")
            continue

    # Convert the list to a DataFrame
    df = pd.DataFrame(data)

    return df
