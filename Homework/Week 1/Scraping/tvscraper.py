#!/usr/bin/env python
# Name: Yoran Tijburg
# Student number: 11384433
"""
This script scrapes IMDB and outputs a CSV file with highest rated tv series.
"""

import csv
import re
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq

TARGET_URL = "http://www.imdb.com/search/title?num_votes=5000,&sort=user_rating,desc&start=1&title_type=tv_series"
BACKUP_HTML = 'tvseries.html'
OUTPUT_CSV = 'tvseries.csv'


def extract_tvseries(dom):
    """
    Extract a list of highest rated TV series from DOM (of IMDB page).
    Each TV series entry should contain the following fields:
    - TV Title
    - Rating
    - Genres (comma separated if more than one)
    - Actors/actresses (comma separated if more than one)
    - Runtime (only a number!)
    """

    Client = uReq(TARGET_URL)
    page_html = Client.read()
    Client.close()

    # parse over the html file
    soup_page = BeautifulSoup(page_html, "html.parser")

    # makes a empty list to store all the information
    series = []

    # takes each serie from the list
    tvseries = soup_page.findAll("div",{"class":"lister-item-content"})
    
    # iterate over each tvserie in the list of tvseries
    for tvserie in tvseries:
        
        # get the tv title
        tv_title = tvserie.h3.a.text

        # get the rating
        rating = tvserie.div.div.text.strip()
        
        # get the genres
        genres = tvserie.p.find("span", {"class":"genre"}).text.strip()
        
        # find all the stars in the serie
        stars_html = tvserie.findAll("a", href=re.compile("name"))
        
        # make empty list to store the stars in
        stars = []

        # iterate over each star and store them to the stars list
        for star in stars_html:
            star_names = star.text
            stars.append(star_names)
        
        stars = ",".join(stars)

        # get the runtime in numbers
        runtime = tvserie.p.find("span", {"class":"runtime"}).text.strip("min")

        # store all the information in the series list
        series.append((tv_title, rating, genres, stars, runtime))

    return series


def save_csv(outfile, tvseries):
    """
    Output a CSV file containing highest rated TV-series.
    """
    writer = csv.writer(outfile)
    writer.writerow(['Title', 'Rating', 'Genre', 'Actors', 'Runtime'])

    # write the information to the disk 
    extract_tvseries(dom)
    for tv_title, rating, genres, stars, runtime in tvseries:
        writer.writerow([tv_title, rating, genres, stars, runtime])


def simple_get(url):
    """
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
        print('The following error occurred during HTTP GET request to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


if __name__ == "__main__":

    # get HTML content at target URL
    html = simple_get(TARGET_URL)

    # save a copy to disk in the current directory, this serves as an backup
    # of the original HTML, will be used in grading.
    with open(BACKUP_HTML, 'wb') as f:
        f.write(html)

    # parse the HTML file into a DOM representation
    dom = BeautifulSoup(html, 'html.parser')

    # extract the tv series (using the function you implemented)
    tvseries = extract_tvseries(dom)

    # write the CSV file to disk (including a header)
    with open(OUTPUT_CSV, 'w', newline='') as output_file:
        save_csv(output_file, tvseries)