# amazon-scrapper
A simple scrapper to scrape data of any category of products from amazon.com. The script of the scraper is written in python using BeautifulSoup Library

## Working
The scraper is a command line scraper that requires the user to enter a keyword/productType (ex: laptop). The script searches Amazon for this category of products and scrapes the data of all the results. The data is written stored in a JSON file. The file is updated after every product is scraped.

The following details are scraped for and individual product:
- Name
- Date First Available
- Price
- Description (All the technical details available)
- Reviews (All the reviews of the product, sorted according to star rating with count)

## Schema
```javascript
  {
    "name":String,
    "dateAvailable":String,
    "price":String,
    "description":{
      "Item Height":"String",
      "Item Width":"String",
      "Screen Size":"String",
      "Processor Speed":"String",
      "RAM":"String",
      "Hard Disk Size":"String",
      "Dimensions":"String"
    },
    "reviews":{
      "5 star":{
        "count":"String",
        "reviews_list": Array		
      },
      "4 star":{
        "count":"String",
        "reviews_list":"String"		
      },
      "3 star":{
        "count":"String",
        "reviews_list": Array		
      },
      "2 star":{
        "count":"String",
        "reviews_list": Array		
      },
      "1 star":{
        "count":"String",
        "reviews_list": Array		
      },
      "total":"String"
    }
  }
```

## Dependancies
The following packages need to be installed to use this scraper:
- BeautifulSoup
- pprint
- numpy
- requests
- datetime

You can install the dependancies using pip:

```pip install BeautifulSoup pprint requests datetime numpy```

## Run
Run the script by executing the following:

```python scrape.py laptop```

You can replace 'laptop' with any category\keyword you like. The output will be written to data.json in the same directory
