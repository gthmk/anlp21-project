import sqlite3
import re
import json
import pandas as pd
import time
from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing

def simple_get(url):
    """
    Source: https://realpython.com/python-web-scraping-practical-introduction/
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Source: https://realpython.com/python-web-scraping-practical-introduction/
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    Source: https://realpython.com/python-web-scraping-practical-introduction/
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def parse_data_content_from_url(url, max_retries=5):
    """
    This function parses the content on the given URL webpage and grabs the "data-content"
    from the <div class='js-store'> tag. The data stored in this object includes all content
    hosted on the webpage.
    """
    html = ''
    soup = ''
    attempt_num = 1
    while (html == '' or soup == '') and attempt_num < max_retries:
        try:
            print('Attempting to reach link: {}'.format(url))
            html = simple_get(url)
            soup = BeautifulSoup(html, 'html.parser')
            data_content = json.loads(soup.find("div", {'class':'js-store'})['data-content'])
            print('Succesfully loaded')
            return(data_content)
        except:
            attempt_num+=1
            print('Connection refused on server for link: {}'.format(url))
            print('Retrying for attempt {0}/{1} in 5 seconds'.format(attempt_num, max_retries))
            time.sleep(5)
            continue


def get_metadata_from_top_page(url):
    data_content = parse_data_content_from_url(url)
    tabs = data_content['store']['page']['data']['data']['tabs']
    hits = data_content['store']['page']['data']['data']['hits']

    return (tabs, hits)


def get_multiple_pages(url, n):
    """
    Creates functionality to scrape multiple
    pages up to n
    """
    page_suffix = "&page="
    tabs_list = []
    hits_list = []

    for i in range(n):
        cur_tabs, cur_hits = get_metadata_from_top_page(url + page_suffix + str(i + 1))

        tabs_list += cur_tabs
        hits_list += cur_hits

    return (tabs_list, hits_list)


def parse_chords_from_url(url):
    data = parse_data_content_from_url(url)

    chords = data['store']['page']['data']['tab_view']['wiki_tab']['content']
    song_name = data['store']['page']['data']['tab']['song_name']

    # Matching groups (open tag)(chord pitch)(base note {0 or 1})(chord type)(base note {0 or 1})(closing tag)
    pattern = "(\[ch\])([A-G]+)(\/[A-G]*[b#])*([(?m)|(?m\d)|(?b\d)|(?#\d)|(?maj\d)|(?add\d)|(?sus\d)|(?aug)|(?aug\d)|(?dim)|(?dim\d)]*)(\/[A-G]*[b#])*(\[\/ch\])"
    prog = re.compile(pattern)
    result = prog.findall(chords)

    cleaned_res = result
    for i in range(len(result)):
        # Grabbing groups (chord pitch)(base note)(chord type)(base note)
        cleaned_res[i] = result[i][1] + result[i][2] + result[i][3] + result[i][4]

    # # Grabbing Capo info
    # capo = 0
    # try:
    #     capo = data['store']['page']['data']['tab_view']['meta']['capo']
    # except:
    #     capo = 0

    return (cleaned_res, song_name)


def parse_tab_fields(tab_obj, hit_obj):
    tab_url = tab_obj['tab_url']
    chords, capo = parse_chords_from_url(tab_url)
    tab_dict = {
        'tab_id': int(tab_obj['id']),
        'song_name': re.sub("'", "", tab_obj['song_name']),
        'artist': re.sub("'", "", tab_obj['artist_name']),
        'tonality': tab_obj['tonality_name'],
        'votes': int(tab_obj['votes']),
        'rating': float(tab_obj['rating']),
        'is_acoustic': int(tab_obj['recording']['is_acoustic']),
        'tab_url': tab_obj['tab_url'],
        'artist_url': tab_obj['artist_url'],
        'hit_id': int(hit_obj['id']),
        'hit_num': int(hit_obj['hits']),
        'chords': ','.join(chords),
        'capo': capo
    }
    return tab_dict


def parse_tab_fields_from_url(tab_url):
    chords, song_name = parse_chords_from_url(tab_url)
    tab_dict = {
        'song_name' : song_name,
        'chords': ','.join(chords),
    }
    return tab_dict


def scrape_ultimate_guitar():

    tabs_list = ['https://tabs.ultimate-guitar.com/tab/ed-sheeran/perfect-chords-1956589']

    tab_dict_list = []

    for i in range(len(tabs_list)):
        tab_dict_list.append(parse_tab_fields_from_url(tabs_list[i]))

    return tab_dict_list


# print(scrape_ultimate_guitar())