import json

import requests
from bs4 import BeautifulSoup
from Scraping import parse_tab_fields_from_url

def tabs_search(query):

    ultimate_guitar = 'https://www.ultimate-guitar.com'
    endpoint = ultimate_guitar + '/search.php?search_type=title&order=&value=' + query

    retries = 0
    while retries < 5:
        try:
            page = requests.get(endpoint)
            break
        except (Timeout, ConnectionError) as e:
            retries += 1
            print("Retry {} for song {}".format(str(retries),str(title_)))
            continue

    if page.status_code == 200:

        tabs_soup = BeautifulSoup(page.text, 'html.parser')
        data_content = json.loads(tabs_soup.find("div", {'class': 'js-store'})['data-content'])
        # results_table = tabs_soup.find('table', class_="tresults")

        list_of_songs = (data_content['store']['page']['data']['results'])

        for song in list_of_songs:

            if 'tab_access_type' in song and song['tab_access_type'] == 'public' \
                    and 'type' in song and song['type'] == 'Chords' \
                    and 'status' in song and song['status'] == 'approved':

                return (song['song_name'],song['tab_url'])

    elif 500 > page.status_code >= 400:
        if page.status_code == 404:
            print("No results found.")
            return ('', '')
        else:
            print("[error] Something went wrong with the request that shouldn't have")
            return ('', '')


    elif page.status_code >= 500:
        print('[error] Looks like ultimate-guitar is having trouble fulfilling the request.')
        print('[error] Try again in a bit or check if the site is up right now.')


def perform_search(raw_query, track_id):
    query = raw_query.replace(" ", "+")
    result = tabs_search(query)

    if result:
        (song_name, tab_url_from_search)= result

        if song_name and tab_url_from_search:
            print("TAB URL",tab_url_from_search)
            final_dict['song_name'].append(raw_query)
            tabs_capo = parse_tab_fields_from_url(tab_url_from_search)
            final_dict['tabs'].append(tabs_capo['chords'])
            final_dict['capo'].append(tabs_capo['capo'])
            final_dict['track_id'].append(track_id)

            print("Parsed : ", tabs_capo)


import csv
import pandas as pd

if __name__ == '__main__':

    filename = "../data/playlist_tracks2.csv"
    output_file = "../data/track_with_tabs_new.csv"

    final_dict = {'song_name': [], 'track_id': [], 'tabs': [], 'capo': []}

    # with open(filename) as file:
    #     for index, line in enumerate(file):
    #         if index == 0:
    #             continue
    #         cols = line.split(",")
    #         print("Song name",cols[5], index)
    #         track_list.append(cols[5])

    df = pd.read_csv(filename)

    track_list = list(df['track_name'])
    track_ids = list(df['track_id'])


    for index, track in enumerate(track_list):
        if track:
            print("Track",index,track)
            perform_search(str(track), track_ids[index])

            h = final_dict.keys()

            if index %500 == 0:
                with open(output_file, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile, delimiter=',')
                    csvwriter.writerow(h)
                    for row in range(len(final_dict[list(h)[0]])):
                        csvwriter.writerow([final_dict[key][row] for key in h])

    header = final_dict.keys()
    no_rows = len(final_dict[list(header)[0]])

    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(header)
        for row in range(no_rows):
            csvwriter.writerow([final_dict[key][row] for key in header])

    # perform_search('hey there delilah')