import platform
import unittest

import psycopg2
import os
from testing import postgresql

import processing
import testing.postgresql
import pandas as pd
import numpy as np


class TestGetFromPostgres(unittest.TestCase):
    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        self.conn = psycopg2.connect(**self.postgresql.dsn())
        cur = self.conn.cursor()
        cur.execute(self.get_create_users())
        cur.execute(self.get_create_relations())
        self.conn.commit()
        cur.execute("INSERT INTO users VALUES ('33', 'Kircheis', 10, 10, 10)")
        cur.execute("INSERT INTO relations (id_source, id_destination,"
                    "tweet_id, type, content, query) VALUES ('33', '34', '1234', 'follow', '', 'logh')")
        cur.close()

    def tearDown(self):
        self.conn.close()
        if platform.system() == 'Windows':
            os.system("taskkill /f /pid " + str(self.postgresql.server_pid))
        else:
            self.postgresql.stop()

    @staticmethod
    def get_create_users():
        return """CREATE TABLE users (
                id VARCHAR(30) PRIMARY KEY,
                screen_name VARCHAR(50),
                followers_count INTEGER,
                friends_count INTEGER,
                favourites_count INTEGER
            );"""

    @staticmethod
    def get_create_relations():
        return """CREATE TABLE relations (
                id SERIAL PRIMARY KEY,
                id_source VARCHAR(30),
                id_destination VARCHAR(30),
                tweet_id VARCHAR(30),
                type VARCHAR(10),
                content TEXT,
                query VARCHAR(50),
                process_time TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE
            );"""

    def test_getDBdata(self):
        users, relations = processing.getDBData(self.conn)
        self.assertTrue(users.equals(pd.DataFrame([{"id": '33', "screen_name": "Kircheis",
                                                    "followers_count": 10, "friends_count": 10,
                                                    "favourites_count": 10}])) &
                        relations.equals(pd.DataFrame([{"id": 1, "id_source": "33", "id_destination": "34",
                                                    "tweet_id": '1234', "type": 'follow', "content": "",
                                                    "query": "logh", "process_time": None, "created_at": None}])))


class TestMain(unittest.TestCase):
    def test_clean(self):
        # given
        text = "for many, &quot;hell&quot; is a <i>fiery</i> place of " \
               "eternal torment, for others it's \n <a href=\"twitter.com\" \\" \
               "class=\"twitter-link\">twitter</a>"

        # when
        cleaned = processing.clean(text)
        # then
        self.assertEqual(cleaned, "for many, \"hell\" is a  fiery place of eternal torment, for others it\'s  Link.")

    def test_makeSentences(self):
        # given
        text = "To be quite frank, one does need to have a rather significant amount of " \
               "intellect to comprehend Richard & Mortimer. Why, just yesterday I attempted " \
               "to show my cousin (who has just entered his seventh year) the episode where the " \
               "titular character, Rick, turns himself into a pickled cucumber."
        # when
        split = processing.makeSentences(text)
        # then
        self.assertEqual(split, ['To be quite frank, one does need to have a rather significant '
                                 'amount of intellect to comprehend Richard & Mortimer.',
                                 'Why, just yesterday I attempted to show my cousin (who has just '
                                 'entered his seventh year) the episode where the titular character, Rick, '
                                 'turns himself into a pickled cucumber.'])

    def test_predict(self):
        self.assertGreaterEqual(processing.predict("I love gaming, it's the best thing ever!"), 0.9)

    def test_getScore(self):
        self.assertGreaterEqual(processing.getScore("I love gaming! It's the best thing ever!"), 1.8)

    def test_createUserMapping(self):
        # given
        users = pd.DataFrame([{"id": 33,
                               "screen_name": "Yang Wen-li",
                               "followers_count": 1978,
                               "friends_count": 1920,
                               "favourites_count": 2005},
                              {"id": 34,
                               "screen_name": "Julian Mintz",
                               "followers_count": 1978,
                               "friends_count": 1920,
                               "favourites_count": 2005},
                              {"id": 20,
                               "screen_name": "Reinhard von Lohengramm",
                               "followers_count": 776,
                               "friends_count": 25,
                               "favourites_count": 801},
                              {"id": 21,
                               "screen_name": "Siegfried Kircheis",
                               "followers_count": 776,
                               "friends_count": 25,
                               "favourites_count": 801}
                              ])
        # then
        pd.testing.assert_frame_equal(processing.createUserMapping(users),
                                      pd.DataFrame([{"X_id": 0, "twitter_id": 33},
                                                    {"X_id": 1, "twitter_id": 34},
                                                    {"X_id": 2, "twitter_id": 20},
                                                    {"X_id": 3, "twitter_id": 21}]))

        def test_createX(self):
            # given
            users = pd.DataFrame([{"id": 33,
                                   "screen_name": "Yang Wen-li",
                                   "followers_count": 1978,
                                   "friends_count": 1920,
                                   "favourites_count": 2005},
                                  {"id": 34,
                                   "screen_name": "Julian Mintz",
                                   "followers_count": 1978,
                                   "friends_count": 1920,
                                   "favourites_count": 2005},
                                  {"id": 20,
                                   "screen_name": "Reinhard von Lohengramm",
                                   "followers_count": 776,
                                   "friends_count": 25,
                                   "favorites_count": 801},
                                  {"id": 21,
                                   "screen_name": "Siegfried Kircheis",
                                   "followers_count": 776,
                                   "friends_count": 25,
                                   "favorites_count": 801}
                                  ])
            relations = pd.DataFrame([{"id_source": 33, "id_destination": 34, "tweet_id": None,
                                       "type": "follow", "content": None},
                                      {"id_source": 34, "id_destination": 33, "tweet_id": None,
                                       "type": "follow", "content": None},
                                      {"id_source": 20, "id_destination": 21, "tweet_id": None,
                                       "type": "follow", "content": None},
                                      {"id_source": 21, "id_destination": 20, "tweet_id": None,
                                       "type": "follow", "content": None}])
            # then
            self.assertEqual(processing.createX(relations, processing.createUserMapping(users)),
                             np.array([[0., 0.01, 1., 1.],
                                       [0.01, 0., 1., 1.],
                                       [1., 1., 0., 0.01],
                                       [1., 1., 0.01, 0.]]))


if __name__ == '__main__':
    unittest.main()
