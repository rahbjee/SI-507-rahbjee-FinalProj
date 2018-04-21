import requests
import json
import sqlite3
from sqlite3 import Error
import secrets
import plotly.plotly as py
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import storage
#================== First setup & retreive data from cache file ================
CACHE_FNAME = 'cache.json'

try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params={}):
    unique_ident = params_unique_combination(baseurl,params)
    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Data deteted in the cache, retreiving now...")
        return CACHE_DICTION[unique_ident]
    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]
#========================= Utility functions start here =====================
# get_location utilizes the Google Natural Language API (google.cloud.language module) to assess each title and extract location string only
def get_location(text):
    client = language.LanguageServiceClient()

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')
    locationNameList = []
    for entity in entities:
        if entity_type[entity.type] == "LOCATION" and entity.name != "OC":
            locationNameList.append(entity.name)
        # print('=' * 20)
        # print(u'{:<16}: {}'.format('name', entity.name))
        # print(u'{:<16}: {}'.format('type', entity_type[entity.type]))
        # print(u'{:<16}: {}'.format('metadata', entity.metadata))
        # print(u'{:<16}: {}'.format('salience', entity.salience))
        # print(u'{:<16}: {}'.format('wikipedia_url',
        #       entity.metadata.get('wikipedia_url', '-')))
    if len(locationNameList) == 0:
        locationNameStr = "Couldn't detect the location information from the Post title"
    else:
        locationNameStr = ' '.join(locationNameList)
    return locationNameStr

#GET Google Places API key from secrets Python file
GP_APIkey = secrets.GP_APIkey
#Access Google Places API to Text Search for the derived location
def google_places_for_post(reddit_post):
    global GP_APIkey
    GP_TextSearch_baseurl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='
    GPSearch_suffix = '&radius=10000&key='+GP_APIkey
    siteParams = (reddit_post.location).replace(' ', '+')
    try:
        GP_response_str = make_request_using_cache(GP_TextSearch_baseurl+siteParams+GPSearch_suffix)
        if GP_response_str['status'] == "ZERO_RESULTS":
            placeTup = ('No results found',)
        else:
            Place_lat = GP_response_str['results'][0]['geometry']['location']['lat']
            Place_lng = GP_response_str['results'][0]['geometry']['location']['lng']
            Place_id = GP_response_str['results'][0]['place_id']
            Place_name = GP_response_str['results'][0]['name']
            placeTup = (Place_name,Place_lat,Place_lng,Place_id)
    except:
        placeTup = ('No results found',)
    return placeTup
#=========== Class definitions for our Posts & Places objects =========
class RedditPost:

    def __init__(self,author,title="",url="",gilded=0,score=0,location=""):
        self.author = author
        self.title = title
        self.gilded = gilded
        self.url = url
        self.score = score
        self.location = get_location(title)

    def __str__(self):
        return "Reddit EarthPorn Post: {}, Located: {}, Score: {}".format(self.title,self.location,self.score)

class Place:

    def __init__(self,name,postId,lat=0,lon=0,placeId="Unknown"):
        self.name = name
        self.postId = postId
        self.lat = lat
        self.lon = lon
        self.placeId = placeId

#============Create, Connect, & Correctly Populate Databases"
# Create & connect to a sqlite database with file name 'PostPlaces.db'
DBNAME = 'postPlaces.db'
try:
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Posts';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Location';
    '''
    cur.execute(statement)
    conn.commit()
except Error as e:
    print(e)

#Create the relevant tables for our objects
try:
    statement = '''CREATE TABLE Posts (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'Author' TEXT NOT NULL,
        'Title' TEXT NOT NULL,
        'GildedId' INTEGER NOT NULL,
        'ImageUrl' TEXT NOT NULL,
        'Rating' REAL NOT NULL,
        'Location' TEXT NOT NULL,
        'LocationId' INTEGER
        );
    '''
    cur.execute(statement)
except Error as e:
    print(e)
try:
    statement = '''CREATE TABLE Location (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'PlaceName' TEXT NOT NULL,
        'PostId' INTEGER NOT NULL,
        'Latitude' REAL,
        'Longitude' REAL,
        'PlaceId' INTEGER NOT NULL
        );
    '''
    cur.execute(statement)
except Error as e:
    print(e)

#Gather data from cache / request & populate the DB
reddit_EarthPornAPI_url = 'https://api.reddit.com/r/earthporn/'
#make_request_using_cache(reddit_EarthPornAPI_url)
ignore_firstpost = False
i = 1
list_of_posts = []
list_of_places = []
for listing in CACHE_DICTION[reddit_EarthPornAPI_url]['data']['children']:
    if ignore_firstpost:
        postTitle = listing['data']['title']
        postAuthor = listing['data']['author']
        postURL = listing['data']['url']
        postGilded = listing['data']['gilded']
        postScore = listing['data']['score']
        post = RedditPost(postAuthor,postTitle,postURL,postGilded,postScore)
        location = google_places_for_post(post)
        if len(location) > 1:
            postPlace = Place(location[0],i,location[1],location[2],location[3])
            postPlaceTup = (location[0],i,location[1],location[2],location[3])
        else:
            postPlace = Place(location[0],i)
            postPlaceTup = (location[0],i,0,0,"Unknown")
        postTuple = (postAuthor,postTitle,postGilded,postURL,postScore,post.location,postPlace.placeId)
        list_of_posts.append(RedditPost)
        list_of_places.append(postPlace)
        #insert into database
        statement = "INSERT INTO Posts VALUES (NULL, ?,?,?,?,?,?,?)"
        cur.execute(statement, postTuple)
        conn.commit()
        statement = "INSERT INTO Location VALUES (NULL, ?,?,?,?,?)"
        cur.execute(statement, postPlaceTup)
        conn.commit()
        i = i+1
    ignore_firstpost = True


#================================Plotly========================================
def plot_places(place_list):
    lat_values = []
    lon_values = []
    text_values = []
    try:
        for eachPlace in place_list:
            lat_values.append(eachPlace.lat)
            lon_values.append(eachPlace.lon)
            text_values.append(eachPlace.name)
        trace2 = dict(
                type = 'scattergeo',
                locationmode = 'ISO-3',
                lon = lon_values,
                lat = lat_values,
                text = text_values,
                mode = 'markers',
                marker = dict(
                    size = 10,
                    symbol = 'diamond',
                    color = 'red'
                ))
        data = [trace2]
        min_lat = 10000
        max_lat = -10000
        min_lon = 10000
        max_lon = -10000
        for str_v in lat_values:
            v = float(str_v)
            if v < min_lat:
                min_lat = v
            if v > max_lat:
                max_lat = v
        for str_v in lon_values:
            v = float(str_v)
            if v < min_lon:
                min_lon = v
            if v > max_lon:
                max_lon = v

        center_lat = (max_lat+min_lat) / 2
        center_lon = (max_lon+min_lon) / 2

        max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
        padding = max_range * .75
        lat_axis = [min_lat - padding, max_lat + padding]
        lon_axis = [min_lon - padding, max_lon + padding]
        layout = dict(
                title = 'Earth Porn Plotted',
                geo = dict(
                    scope='world',
                    projection=dict( type='mercator' ),
                    showland = True,
                    landcolor = "rgb(250, 250, 250)",
                    subunitcolor = "rgb(100, 217, 217)",
                    countrycolor = "rgb(217, 100, 217)",
                    lataxis = {'range': lat_axis},
                    lonaxis = {'range': lon_axis},
                    center= {'lat': center_lat, 'lon': center_lon },
                    countrywidth = 3,
                    subunitwidth = 3
                ),
            )
        fig = dict(data=data, layout=layout )
        py.plot( fig, validate=False, filename='Earth Porn Plotted')
    except:
        print("No lat/long coordinates found for this site")
    pass

#plot_places(list_of_places)
