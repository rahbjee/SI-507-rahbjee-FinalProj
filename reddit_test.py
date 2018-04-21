import reddit as reddit
import sqlite3
import unittest

# class TestPostPull(unittest.TestCase):
#
#     def post_is_in_state_list(self, site_name, site_type, site_list):
#         for s in site_list:
#             if site_name == s.name and site_type == s.type:
#                 return True
#         return False
#
#     def get_site_from_list(self, site_name, site_list):
#         for s in site_list:
#             if site_name == s.name:
#                 return s
#         return None
#
#     def setUp(self):
#         self.mi_site_list = get_sites_for_state('mi')
#         self.az_site_list = get_sites_for_state('az')
#         self.isle_royale = self.get_site_from_list('Isle Royale', self.mi_site_list)
#         self.lake_mead = self.get_site_from_list('Lake Mead', self.az_site_list)
#
#     def test_basic_search(self):
#         self.assertEqual(len(self.mi_site_list), 7)
#         self.assertEqual(len(self.az_site_list), 24)
#
#         self.assertTrue(self.site_is_in_state_list('Isle Royale',
#             'National Park', self.mi_site_list))
#         self.assertFalse(self.site_is_in_state_list('Isle Royale',
#             'National Park', self.az_site_list))
#
#         self.assertTrue(self.site_is_in_state_list('Lake Mead',
#             'National Recreation Area', self.az_site_list))
#         self.assertFalse(self.site_is_in_state_list('Lake Mead',
#             'National Recreation Area', self.mi_site_list))
#
#     def test_addresses(self):
#         self.assertEqual(self.isle_royale.address_street, '800 East Lakeshore Drive')
#         self.assertEqual(self.isle_royale.address_city, 'Houghton')
#         self.assertEqual(self.isle_royale.address_zip, '49931')
#
#         self.assertEqual(self.lake_mead.address_street, '601 Nevada Way')
#         self.assertEqual(self.lake_mead.address_city, 'Boulder City')
#         self.assertEqual(self.lake_mead.address_zip, '89005')
#
#     def test_str(self):
#         self.assertEqual(str(self.lake_mead), "Lake Mead (National Recreation Area): 601 Nevada Way, Boulder City, NV 89005")
#         self.assertEqual(str(self.isle_royale), "Isle Royale (National Park): 800 East Lakeshore Drive, Houghton, MI 49931")
#
#
# class TestNearbySearch(unittest.TestCase):
#
#     def place_is_in_places_list(self, place_name, places_list):
#         for p in places_list:
#             if place_name == p.name:
#                 return True
#         return False
#
#     def test_nearby_search(self):
#         site1 = NationalSite('National Monument',
#             'Sunset Crater Volcano', 'A volcano in a crater.')
#         site2 = NationalSite('National Park',
#             'Yellowstone', 'There is a big geyser there.')
#
#         nearby_places1 = get_nearby_places_for_site(site1)
#         nearby_places2 = get_nearby_places_for_site(site2)
#
#         self.assertTrue(self.place_is_in_places_list('Cinder Lake Landfill', nearby_places1))
#         self.assertTrue(self.place_is_in_places_list('Yellowstone General Store', nearby_places2))

class TestDatabase(unittest.TestCase):

    def test_post_table(self):
        DBNAME = 'postPlaces.db'
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = 'SELECT Author,Title,Rating,Location FROM Posts ORDER BY Rating DESC'
        results = cur.execute(sql)
        result_list = results.fetchall()
        author_list = []
        title_list = []
        for eachResult in result_list:
            a = eachResult[0]
            t = eachResult[1]
            author_list.append(a)
            title_list.append(t)

        self.assertIn('grantplace', author_list)
        self.assertIn('Larch Heaven, Washington State [OC] [2398 x 3000]', title_list)
        self.assertEqual(result_list[0][2], 42553.0)
        self.assertEqual(result_list[0][3], 'Forest UK Wales')
        self.assertEqual(len(result_list), 100)
        conn.close()

    def test_location_table(self):
        DBNAME = 'postPlaces.db'
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = 'SELECT PlaceName,Latitude, PlaceId FROM Location ORDER BY Latitude DESC'
        results = cur.execute(sql)
        result_list = results.fetchall()
        place_list = []
        for eachResult in result_list:
            p = eachResult[0]
            place_list.append(p)
        self.assertIn('Zion National Park', place_list)
        self.assertEqual(result_list[0][0], 'Dettifoss')
        self.assertEqual(round(result_list[0][1]), round(65.8146662))
        self.assertEqual(result_list[0][2], 'ChIJuU9fzooGzUgReiMomHV4QkA')
        self.assertEqual(len(result_list), 100)
        conn.close()

    def test_PostObj(self):
        DBNAME = 'postPlaces.db'
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = 'SELECT Author,Title,ImageUrl,GildedId, Rating FROM Posts ORDER BY Rating DESC'
        results = cur.execute(sql)
        result_list = results.fetchall()
        post_list = []
        post1 = reddit.RedditPost(result_list[0][0],result_list[0][1],result_list[0][2],result_list[0][3],result_list[0][4])
        self.assertEqual(post1.url, 'https://i.redd.it/7x4vvfobkwq01.jpg')
        self.assertEqual(post1.score, 42553.0)
        self.assertEqual(post1.title, 'Guardians of the Forest, Wales, UK (OC) [864x1080]')
        self.assertEqual(post1.author, 'simonbaxter')
        self.assertEqual(post1.gilded, 0)
        conn.close()

unittest.main()
