Welcome to Rahul Bonnerjee's Final Project for SI 507
This python program makes requests to Reddit's API as well as the Natural Language Cloud & Places APIs offered by Google to gather data on the posts of the /r/EarthPorn subreddit, parse their location information, and then plot those places using Plotly

Data Sources: Reddit API for post data & Google Places API for places data
IMPORTANT:  To run this program on your system, will need an to create a project authorized to use the Places & Natural Language API in the Google Developers Console (https://console.cloud.google.com/) in order to provide credentials to your application (https://cloud.google.com/docs/authentication/production).  All in all you will need an authorized API key for Google Places as well as a service account that will provide a .json file containing another private key (more info here: https://console.cloud.google.com/apis/credentials/serviceaccountkey)

I have not included my API keys in this repo, for the sake of my own privacy.

Plotly also has you create an account with them, to track your usage of their API.  I have again omitted my information, and you must link this program to your personal plotly/professional account.

After obtaining your credentials you must install the proper modules in order for the program to run correctly.  The requirements.txt contains all of this information for you to install on you virtual environment

There is no interactivity programmed into this project, simply data requesting from reddit, caching, storing, processing and visualization using JSON, OAuth, SQLite3, and plotly.

Essentially this program is split into 1 main file and 1 unittest file.
The first part of the reddit.py file contains utility functions that are used to make requests / set up the cache & parse post titles for specific location information. (lines 13-102)
Followed by Class definitions of a RedditPost and a Place object, each representing an entry into the connected SQLite Databases(lines 104-125)
So then comes our declaration, creation, insertion, and ultimately connection to our postPlaces database (lines 128-208)
Finally for the list created from our previous section, we plot all of the places we obtained coordinates from in the last part. (lines 212-280)

The reddit_test.py function contains three unittests to test if the database tables are created correctly, and whether they can be mapped to a RedditPost object correctly.
