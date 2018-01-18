from pprint import pprint
import numpy as np
from bs4 import BeautifulSoup
import requests, json, re, sys, datetime

def getProductDetails(id):
    url = base+'dp/'+id;
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml");
    product = {}
    product["_id"] = id
    if(soup.find('span', id='productTitle') == None or soup.find('a', id='brand') == None or soup.find('div', id="prodDetails") == None or len(soup.findAll('span', id=re.compile('^priceblock_(deal|sale|our)price$'))) == 0):
        print "\tNot Relevant"
        return {}
    product["name"] = parse(soup.find('span', id='productTitle').text)
    product["brand"] = parse(soup.find('a', id='brand').text)
    product["price"] = float(parse(soup.findAll('span', id=re.compile('^priceblock_(deal|sale|our)price$'))[0].text.replace(',','')))

    product["dateAvailable"] = parse(soup.find('div', id="prodDetails").find('tr', attrs={'class':'date-first-available'}).find('td', attrs={"class":"value"}).text)

    tags = {}
    for tr in soup.select('div#prodDetails div.pdTab table tbody tr'):
        try:
            if(tr.find('td', attrs={"class":"label"}) == None):
                continue;
            key = parse(tr.find('td', attrs={"class":"label"}).text)
            value = parse(tr.find('td', attrs={"class":"value"}).text)
            tags[key] = value
        except AttributeError:
            break
    if "Processor Speed" not in tags:
        print "\tNot Relevant"
        return {}
    product["description"] = tags;

    if(soup.find('div', id="reviewSummary").find('span', id='dp-no-customer-review-yet') == None):
        reviews = {
            "total": parse(soup.find('div', id="reviewSummary").find('span', attrs={'class':'totalReviewCount'}).text)
        }
        for tr in soup.find('table', id="histogramTable").find_all('tr'):
            if(tr.find('td', attrs={"class":"a-text-right"}).a == None or tr.find('td', attrs={"class":"aok-nowrap"}).a == None):
                continue;
            key = parse(tr.find('td', attrs={"class":"aok-nowrap"}).a.attrs['title'])
            value = parse(tr.find('td', attrs={"class":"a-text-right"}).a.text)
            reviews[key] = {"count": int(value.replace(',',"")), "reviews_list": []}

        # get all reviews with content and date
        j = 1
        while(True):
            review_url = base+'product-reviews/'+id +'?pageNumber=' + str(j)
            response = requests.get(review_url, headers=headers)
            review_soup = BeautifulSoup(response.content, "lxml");
            if(review_soup.find('div', id="cm_cr-review_list") == None):
                break
            if(review_soup.find('div', id="cm_cr-review_list").find('div', attrs={'class':'no-reviews-section'}) != None):
                break
            for div in review_soup.select('div#cm_cr-review_list > div'):
                rev = {}
                try:
                    if('id' not in div.attrs):
                        continue
                    rev["_id"] = div.attrs['id']
                    rev["title"] = parse(div.find('a', attrs={"data-hook":"review-title"}).text)
                    rev["content"] = div.find('span', attrs={'data-hook':'review-body'}).text.replace('<br>','\n')
                    rev["author"] = parse(div.find('a', attrs={"data-hook":"review-author"}).text)
                    rev["date"] = parse(div.find('span', attrs={"data-hook":"review-date"}).text.replace('on',''))
                    rating = str(parse(div.find('i', attrs={"data-hook":"review-star-rating"}).find('span').text))[0]
                    reviews[rating + " star"]["reviews_list"].append(rev)
                except AttributeError:
                    continue
            print "\tReview page "+str(j)+" retrieved"
            j+=1
        product["reviews"] = reviews
    else:
        product["reviews"] = {}
    return product

def parse(str):
    return str.strip().replace('\n','')

def searchCategory(category, page):
    url = base + 's?keyword=' + category
    # response = requests.get(url, headers=headers, timeout=5)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml");
    if(soup.find('h1', id="noResultsTitle") != None):
        return False
    for li in soup.find('ul', id="s-results-list-atf").find_all('li'):
        if(li.attrs == {} or "data-asin" not in li.attrs):
            continue
        frontier.append(li.attrs["data-asin"])
    return True


##################################### MAIN ######################################
base = 'https://www.amazon.in/'
frontier = []
data  = []

classifier_data = []
classifier_labels = []

results_fetched = True;
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'}
AJAX_headers = {"X-Requested-With":"XMLHttpRequest", "User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"}
keyword = 'laptop'
if(len(sys.argv)>1):
    keyword = str(sys.argv[1])
print "\nsearching for keyword '"+keyword+"'"

i = 1
while(results_fetched):
    print "Retrieving page " +str(i)+" results"
    results_fetched = searchCategory(keyword, str(i))
    i+=1

frontier = list(set(frontier))                                  #removing duplicate entires

open('data.json', 'w').close()                                  #clear file contents
with open('data.json', 'a') as outfile:
    outfile.write('[')
    for i in frontier:
        print "Fetching Data for Product Id: " + i
        json.dump(getProductDetails(i), outfile)                #write each product data to file
        outfile.write(',')
    outfile.seek(0,2)
    size = outfile.tell()
    outfile.truncate(size-1)                                    #remove trailing comma
    outfile.write(']')                                          #close JSON
print "Data fetched, output written to >> data.json"
