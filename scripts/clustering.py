import genieclust
import pandas as pd
import numpy as np

if __name__ == "__main__":
    X = np.loadtxt("data/X.csv", delimiter=",")
    user_map = pd.read_csv("data/user_map.csv")
    X_id = user_map.X_id
    print("Running clustering...")
    gen = genieclust.Genie(100, affinity="precomputed", gini_threshold=0.05)
    labels = gen.fit_predict(X)
    np.savetxt("data/labels.csv", labels, delimiter=",", newline="\n")
    print("Clustering finished...")
