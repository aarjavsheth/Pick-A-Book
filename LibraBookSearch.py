import time
import tkinter
import tkinter.scrolledtext as text
import urllib.request
import json
from cachetools import TTLCache

cacheKey = ''

# Caches(TTL)
queryCache = TTLCache(maxsize = 400, ttl = 60)
resultsCache = TTLCache(maxsize = 1000, ttl = 60)

# API Search Query Class
class SearchQuery:     
    def __init__(self, isbn, title, authors):
        self.isbn = isbn
        self.title = title
        self.authors = authors

    # Function to perform the API search query
    def performQuery(self):
        global cacheKey,queryCache
        
        # Query URL
        url = 'https://www.googleapis.com/books/v1/volumes?q='
        originalUrl = url
        if self.isbn != '':
            url = url + 'isbn:' + self.isbn
        if self.title != '':
            if url != originalUrl:
                url = url + '&'
            url = url + 'title:'
            for i in range(0, len(self.title)):
                if self.title[i] == ' ':
                    url = url + '%20'
                else:
                    url = url + self.title[i]
        if len(self.authors) != 0:
            if url != originalUrl:
                url = url + '&'
            for index, name in enumerate(self.authors):
                for i in range(0, len(name)):
                    if name[i] == ' ':
                        url = url + '%20'
                    elif name[i] == ',':
                        url = url + '%27'
                    else:
                        url = url + name[i]
        
        relevantInformation = []   # To store the ISBN, Title & Authors from each result
        cacheKey = url
        
        # Checking if query has already been cached
        if url in queryCache:
            start = time.time()
            relevantInformation = queryCache[url]
            end = time.time()
            print('Query fetched from cache memory! Time taken: ' + str(end-start) + ' secs')
            queryCache[url] = relevantInformation
            return relevantInformation
        # Executing query via API and storing JSON results
        else:   
            start = time.time()
            jsonObj = urllib.request.urlopen(url).read()
            end = time.time()
            print('Query fetched via API! Time taken: ' + str(end - start) + ' secs')
            data = json.loads(jsonObj)
            
            # Reading results
            if 'items' not in data:
                relevantDataset = []
                return relevantDataset
            relevantDataset = data['items']
            for item in relevantDataset:
                volumeItemset = item['volumeInfo']
                newItem = {}
                if "industryIdentifiers" in volumeItemset:
                    newItem['isbn'] = volumeItemset['industryIdentifiers'][0]['identifier']
                if "title" in volumeItemset:
                    newItem['title'] = volumeItemset['title']
                if "authors" in volumeItemset:
                    newItem['authors'] = volumeItemset['authors']
                if len(newItem) > 0:
                    relevantInformation.append(newItem)
            queryCache[url] = relevantInformation
            return relevantInformation
    

# Class for Displaying Search Results
class SearchOutput:

    def __init__(self, queryItem):
        global queryCache,resultsCache,cacheKey
        self.output_text = ''
        if len(queryItem) != 0:        
            for item in queryItem:
                if 'title' in item:
                    self.output_text = self.output_text + ' Title: ' + item['title'] + '\n'
                if 'isbn' in item:
                    self.output_text = self.output_text + ' ISBN: ' + item['isbn'] + '\n'
                if 'authors' in item:
                    self.output_text = self.output_text + ' Authors: '
                    for j in item['authors']:
                        self.output_text = self.output_text + j +', '
                    self.output_text = self.output_text[:-2]
                self.output_text = self.output_text + '\n\n'
        else:
            self.output_text = 'No Results :('
        
        # Initializing Output Window
        self.output_window = tkinter.Tk()
        self.output_window.title('Books')
        self.output_window.geometry('640x480')
        
        # Adding Widgets
        self.output_box = text.ScrolledText(self.output_window, wrap = tkinter.WORD, width = 540, height = 420)
        self.output_box.pack()
        self.output_box.insert(tkinter.INSERT, self.output_text)
        
        # Caching output
        if len(queryItem) != 0:
            resultsCache[cacheKey] = self.output_text


# Class to Search for Books
class SearchWindow:
    
    def __init__(self):
        
        # Creating new Search Window
        self.search_window = tkinter.Tk()
        self.search_window.title('Search')
        self.search_window.geometry('400x180')
        
        # Add Widgets
        self.title_label = tkinter.Label(self.search_window, text = 'Title', font = ('Segoe UI',15)).grid(row = 0)
        self.title_entry = tkinter.Entry(self.search_window, text = '', font = ('Times New Roman', 15), width = 30)
        self.title_entry.grid(row = 0,column = 1)
        self.isbn_label = tkinter.Label(self.search_window, text = 'ISBN', font = ('Segoe UI',15)).grid(row = 1)
        self.isbn_entry = tkinter.Entry(self.search_window, text = '', font = ('Times New Roman',15), width = 30)
        self.isbn_entry.grid(row = 1, column = 1)
        self.authors_label = tkinter.Label(self.search_window, text = 'Authors', font = ('Segoe UI',15)).grid(row= 2)
        self.authors_entry = tkinter.Entry(self.search_window, text = '', font = ('Times New Roman',15), width = 30)
        self.authors_entry.grid(row = 2, column = 1)
        self.author_warning = tkinter.Label(self.search_window, text = 'Seperate authors by comma(,)', font = ('Segoe UI', 8)).grid(row = 3, column = 1)
        self.submit_button = tkinter.Button(self.search_window, text = 'Submit', font = ('Roboto',15), command = self.executeSearch).grid(row = 4,column = 1)   #Submit Button

    def executeSearch(self):
        searchISBN = self.isbn_entry.get()
        searchTitle = self.title_entry.get()
        searchAuthors = self.authors_entry.get()
        if (searchISBN != '') or (searchTitle != '') or searchAuthors != '':
            queryItem = SearchQuery(searchISBN,searchTitle,searchAuthors)
            results = queryItem.performQuery()
            SearchOutput(results)

class HistoryWindow:
    
    def __init__(self):    
        global resultsCache

        # Initializing History Window
        self.history = tkinter.Tk()
        self.history.title('History')
        self.history.geometry('640x480')
        
        # Adding Widgets to History Window
        self.history_box =  text.ScrolledText(self.history, wrap = tkinter.WORD, width = 480, height = 420)
        self.history_box.pack()
        self.history_helpful_label = tkinter.Label(self.history, text = 'Past 10 minutes history', font = ('Segoe UI', 15)).pack()
        
        self.history_text = ''
        list_of_keys = resultsCache.keys()
        for i in list_of_keys:
            self.history_text = self.history_text + resultsCache[i]
        self.history_box.insert(tkinter.INSERT, self.history_text)
        
# Home Window        
class HomeWindow:
    
    def __init__(self):
        
        # Initializing the Home Window
        self.home = tkinter.Tk()
        self.home.title("Home")
        self.home.geometry('1280x720')
        
        # Adding Widgets To Home Window
        self.top_heading  =  tkinter.Label(self.home, text = 'Pick-A-Book', font = ('Open Sans', 50)).pack()
        self.top_tagline  = tkinter.Label(self.home, text = 'The right book in the right hands at the right time can change the world', font = ('Segoe UI', 20)).pack()
        self.empty_label1 = tkinter.Label(self.home, text = '', height = 5).pack()    
        self.search_button = tkinter.Button(self.home, text = 'Search Books', font = ('Segoe UI', 20), command = self.openSearchWindow).pack() # Button to open Search Window
        self.empty_label2 = tkinter.Label(self.home, text = '', height = 2).pack()
        self.history_button = tkinter.Button(self.home, text = 'History', font = ('Segoe UI', 20), command = self.openHistoryWindow).pack()    # Button to open History Window
        
    
    def openSearchWindow(self):   # Event listener for Search Button on Home Window
        SearchWindow()
        
    
    def openHistoryWindow(self):  # Event Listener for History Button on Home Window
        HistoryWindow()


# Initializing the Home Window
home_window = HomeWindow()
home_window.home.mainloop()
