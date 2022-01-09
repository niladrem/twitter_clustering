import psycopg2
from psycopg2 import Error
import pandas as pd
import re
from flair.models import TextClassifier
from flair.data import Sentence
from segtok.segmenter import split_single
import numpy as np

classifier = TextClassifier.load('en-sentiment')

def getDBData(limit=None):
    """Downloads PostgreSQL data into pandas dataframes"""
    connection = None
    users = None
    relations = None
    try:
        connection = psycopg2.connect(user="twitter",
                                     password="twitter",
                                     host="postgres",
                                     port="5432",
                                     database="twitter")
        print("Estabilished connection to PostgreSQL")
        if limit is None:
            users = pd.read_sql("SELECT * from users", connection)
            relations = pd.read_sql("SELECT * from relations", connection)
        else:
            users = pd.read_sql("SELECT * from users limit " + str(limit), connection)
            relations = pd.read_sql("SELECT * from relations limit" + str(limit), connection)
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
    result = text.to_dict()['labels'][0]['confidence']
    if text.to_dict()['labels'][0]['value'] == "NEGATIVE":
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


def createX(rel, user_map, weight_dict="default"):
    """Creates X distance matrix for all users"""
    if weight_dict == "default":
        weight_dict = default_weight_dict
    default_weight_dict = {
        "follow": 50,
        "retweet": 5,
        "like": 10,
        "mention": 10,
        "quote": 5,
        "reply": 10,
        "friend": 50
    }

    for reaction in weight_dict:
        if weight_dict[reaction] == 0:
            weight_dict[reaction] = default_weight_dict[reaction]



    rel = rel.merge(user_map.set_index('twitter_id').rename(columns={'X_id': 'X_id_source'}),
                    how='left', left_on='id_source', right_on='twitter_id')
    rel = rel.merge(user_map.set_index('twitter_id').rename(columns={'X_id': 'X_id_destination'}),
                    how='left', left_on='id_destination', right_on='twitter_id')
    X = np.zeros((len(user_map), len(user_map)))
    for i, r in rel.iterrows():
        X[r['X_id_source'], r['X_id_destination']] += weight_dict[r['type']]
        X[r['X_id_destination'], r['X_id_source']] += weight_dict[r['type']]

    # normalization
    X = 1 / (X + (X == 0))
    return X

if __name__ == "__main__":
    print("Loading data")
    us, rel = getDBData()
    user_map = createUserMapping(us)
    X = createX(rel, user_map)
    np.savetxt("data/X.csv", X, delimiter=",", newline="\n")
    user_map.to_csv("data/user_map.csv")
    us.to_csv("data/users.csv")
    rel.to_csv("data/relations.csv")
    print("Writing data")