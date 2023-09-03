from django.http import HttpResponse
from django.shortcuts import render
from numpy import append
import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
import csv

def get_source(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        return response
    except requests.exceptions.RequestException as e:
        print(e)

def scrape_google(query):
    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)

    links = list(response.html.absolute_links)
    google_domains = ('https://www.google.', 
                      'https://google.', 
                      'https://webcache.googleusercontent.', 
                      'http://webcache.googleusercontent.', 
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.')
    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)
    
    return links

def get_results(query):
    
    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)
    
    return response


def parse_results(response):
    
    css_identifier_result = ".tF2Cxc"
    css_identifier_title = "h3"
    css_identifier_link = ".yuRUbf a"
    css_identifier_text = ".VwiC3b"
    
    results = response.html.find(css_identifier_result)

    output = []
    
    for result in results:

        item = {
            'title': result.find(css_identifier_title, first=True).text, #title
            'link': result.find(css_identifier_link, first=True).attrs['href'], #link
        }
        output.append(item)
    return output


def google_search(query):
    response = get_results(query)
    return parse_results(response)

def to_dataframe(response):
    result = {
        'title' : [],
        'link' : [],
    }
    for item in response:
        result['title'] = append(result['title'], item['title'])
        result['link'] = append(result['link'], item['link'])
    return pd.DataFrame(result)

def write_to_csv(df): 
    return df.to_csv("temp.csv", header=True, sep=',')

def home(request):
    return render(request, 'home.html')

def waiting_room(request):
    term = request.GET.get("searchTerm", "")
    search_res = google_search(term)
    dataf = to_dataframe(search_res)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="result.csv"'
    writer = csv.writer(response)
    writer.writerow(dataf.keys())
    for index, row in dataf.iterrows():
        writer.writerow(row)
    return response