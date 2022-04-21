import os

import psycopg2
from psycopg2 import Error
import pandas as pd
import re
from flair.models import TextClassifier
from flair.data import Sentence
from segtok.segmenter import split_single
import numpy as np
import os
import argparse

classifier = TextClassifier.load('en-sentiment')


def getDBData(query="%", limit=None, custom_conn=None):
    """Downloads PostgreSQL data into pandas dataframes"""
    connection = None
    users = None
    relations = None
    try:
        if custom_conn is None:
            connection = psycopg2.connect(user=os.environ.get("TWT_USER"),
                                          password=os.environ.get("TWT_PASSWORD"),
                                          host=os.environ.get("TWT_HOST"),
                                          port=os.environ.get("TWT_PORT"),
                                          database=os.environ.get("TWT_DATABASE"))
        else:
            connection = custom_conn
        print("Estabilished connection to PostgreSQL")

        users_query = "SELECT * from users where id in (SELECT id_source from relations where query='{}') " \
                      "or id in (SELECT id_destination from relations where query='{}')".format(query, query)
        if limit is None:
            users = pd.read_sql("SELECT * from users where id in (select id_source from relations where query = "
                                "'{}') or id in (select id_destination from public.relations where query = "
                         "'{}')".format(query, query), connection)
            relations = pd.read_sql("SELECT * from relations where query like '%{}%'".format(query), connection)


        else:
            users = pd.read_sql("SELECT * from users where id in (select id_source from relations where query = "
                                "'{}') or id in (select id_destination from public.relations where query = "
                         "'{}') limit ".format(query, query), connection)
            relations = pd.read_sql("SELECT * from relations where query like '%{}%' limit {}".format(query, limit),
                                    connection)
        print("Closed connection to PostgreSQL")
    except(Exception, Error) as e:
        print("Error while connecting to PostgreSQL", e)
    finally:
        if connection:
            connection.close()
            print("Closed connection to PostgreSQL")
    return users, relations


def clean(raw):
    """ Remove hyperlinks and markup """
    result = re.sub("<[a][^>]*>(.+?)</[a]>", 'Link.', raw)
    result = re.sub('&gt;', "", result)
    result = re.sub('&#x27;', "'", result)
    result = re.sub('&quot;', '"', result)
    result = re.sub('&#x2F;', ' ', result)
    result = re.sub('<p>', ' ', result)
    result = re.sub('</i>', '', result)
    result = re.sub('&#62;', '', result)
    result = re.sub('<i>', ' ', result)
    result = re.sub("\n", '', result)
    return result


def makeSentences(text):
    """ Break apart text into a list of sentences """
    sentences = [sent for sent in split_single(text)]
    return sentences


def predict(sentence):
    """ Predict the sentiment of a sentence """
    if sentence == "":
        return 0
    text = Sentence(sentence)
    # stacked_embeddings.embed(text)
    classifier.predict(text)
    result = text.to_dict()['all labels'][0]['confidence']
    if text.to_dict()['all labels'][0]['value'] == "NEGATIVE":
        result = result * (-1)
    return result


def getScore(text):
    """ Call predict on every sentence of a text """
    if text is None:
        return None
    text = clean(text)
    sentences = makeSentences(text)
    results = []
    for i in range(0, len(sentences)):
        results.append(predict(sentences[i]))

    result = sum(results)
    return result


def createUserMapping(us):
    """Creates user mapping between X indexes and twitter ID"""
    user_map = pd.DataFrame(us.id)
    user_map.reset_index(level=0, inplace=True)
    user_map = user_map.rename(columns={'index': 'X_id', 'id': 'twitter_id'})
    return user_map


def createX(rel, user_map, weight_dict="default", use_sentiment=False):
    """Creates X distance matrix for all users"""
    if weight_dict == "default":
        weight_dict = {
            "follow": 50,
            "retweet": 5,
            "like": 10,
            "mention": 10,
            "quote": 5,
            "reply": 10,
            "friend": 50
        }
    rel = rel.merge(user_map.set_index('twitter_id').rename(columns={'X_id': 'X_id_source'}),
                    how='left', left_on='id_source', right_on='twitter_id')
    rel = rel.merge(user_map.set_index('twitter_id').rename(columns={'X_id': 'X_id_destination'}),
                    how='left', left_on='id_destination', right_on='twitter_id')
    X = np.zeros((len(user_map), len(user_map)))
    for i, r in rel.iterrows():
        if use_sentiment:
            if type(r['content']) == str:
                score = getScore(r['content'])
                X[r['X_id_source'], r['X_id_destination']] += weight_dict[r['type']] * score
                X[r['X_id_destination'], r['X_id_source']] += weight_dict[r['type']] * score
            else:
                X[r['X_id_source'], r['X_id_destination']] += weight_dict[r['type']]
                X[r['X_id_destination'], r['X_id_source']] += weight_dict[r['type']]
        else:
            X[r['X_id_source'], r['X_id_destination']] += weight_dict[r['type']]
            X[r['X_id_destination'], r['X_id_source']] += weight_dict[r['type']]
    if use_sentiment:
        X[X < 0] = 0
    # normalization
    X = 1 / (X + (X == 0))
    np.fill_diagonal(X, 0)
    return X