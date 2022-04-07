import argparse
import genieclust
import pandas as pd
import numpy as np
import psycopg2
import processing


def parse_args():  # pragma: no cover
    parser = argparse.ArgumentParser()

    parser.add_argument('--path', default='/shared/data/formatted/')
    parser.add_argument('--remove-processed-files', type=bool, default=False)
    parser.add_argument('--postgres-host', default='localhost')
    parser.add_argument('--postgres-port', default='5432')
    parser.add_argument('--postgres-login', default='twitter')
    parser.add_argument('--postgres-password', default='twitter')
    parser.add_argument('--postgres-database', default='twitter')

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    connection = psycopg2.connect(host=args.postgres_host, database=args.postgres_database, port=args.postgres_port,
                                  user=args.postgres_login, password=args.postgres_password)
    print("Estabilished connection to PostgreSQL")
    print("Loading data")
    us, rel = processing.getDBData(connection)
    user_map = processing.createUserMapping(us)
    X = processing.createX(rel, user_map)
    np.savetxt("data/X.csv", X, delimiter=",", newline="\n")
    user_map.to_csv("data/user_map.csv")
    us.to_csv("data/users.csv")
    rel.to_csv("data/relations.csv")
    print("Writing data")
    X = np.loadtxt("data/X.csv", delimiter=",")
    user_map = pd.read_csv("data/user_map.csv")

