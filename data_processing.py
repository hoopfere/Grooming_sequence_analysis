import pandas as pd
import numpy as np


def df_to_markov(data, counts=False):
    """
    given a dataframe with a column "Behavior type", returns a markov
    chain adjacency matrix representing transitions in that sequence
    """
    
    behaviors = data["behavior"].tolist()
    
    behavior_vals = ["head", "abdominal", "wing", "rubbing", "thorax"]
    frequencies = pd.DataFrame(np.zeros((5, 5)), index=behavior_vals, columns=behavior_vals)
    
    for i in range(len(behaviors)-1):
        curr = behaviors[i]
        next = behaviors[i+1]
        frequencies.loc[next, curr] += 1
    
    if counts:
        return frequencies
    
    normalizing = np.sum(frequencies.values, axis=-1).reshape(-1,1)
    
    probabilities = (frequencies.values)/normalizing
    probabilities = np.nan_to_num(probabilities)
    
    markov = pd.DataFrame(probabilities, index=behavior_vals, columns=behavior_vals)
    
    return markov


def csv_to_dfs(filepath):
    data = pd.read_csv(filepath)
    data = data.query("behavior != 'class_all_grooming'")
    
    dfs = [data[data["file"] == f] for f in pd.unique(data["file"])]

    return dfs


def main():
    df_list = csv_to_dfs("/Users/anu/Documents/carleton/fly_syntax_nlp/SocialIsolationData.csv")
    
    syntax_list = [df_to_markov(df) for df in df_list]
    
    print(syntax_list)
    
if __name__ == "__main__":
    main()