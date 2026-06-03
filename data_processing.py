import pandas as pd
import numpy as np
import h5py

behavior_vals = ["head", "abdominal", "wing", "rubbing", "thorax", "stand"]

def df_to_markov(data, delta=1, counts=False):
    """
    given a dataframe with a column "Behavior type", returns a markov
    chain adjacency matrix representing transitions in that sequence
    """
    
    behaviors = data["behavior"].tolist()
    start_times = data["start_time"].tolist()
    durations = data["duration"].tolist()
    
    frequencies = pd.DataFrame(np.zeros((6, 6)), index=behavior_vals, columns=behavior_vals)
    
    for i in range(len(behaviors)-1):
        curr = behaviors[i]
        next = behaviors[i+1]
        
        if start_times[i+1] - start_times[i] > durations[i] + delta or curr == next:
            frequencies.loc[curr, "stand"] += 1
            frequencies.loc["stand", next] += 1
        
        else:
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
    
    dfs = [data[data["file"] == f].sort_values("start_time") for f in pd.unique(data["file"])]
    return dfs

def get_jaaba_features(filepath):
    with h5py.File(filepath, 'r') as f:
        print("Keys:", list(f.keys()))
        data = f.get('trx/x')
        
        print(data[0][0].value)
    pass 

def get_sequences(filepath, label):
    for df in csv_to_dfs(filepath):
        curr_behaviors = df["behavior"].tolist()[1:]
        prev_behaviors = df["behavior"].tolist()[:-1]
        labels = [label for i in range(len(curr_behaviors))]
        
    return pd.DataFrame()

def get_interbout(filepath):
    breaks = []
    
    for data in csv_to_dfs(filepath):
        data = data.sort_values(by="start_time")
        
        start_times = data["start_time"].tolist()
        durations = data["duration"].tolist()
        
        for i in range(len(start_times)-1):
            breaks.append(start_times[i+1] - start_times[i] - durations[i])
            
    return breaks
        

def mean_markovs(df_list):
    mean_prob = np.zeros((6,6))
    for df in df_list:
        mean_prob += df.values
    mean_prob /= len(df_list)
    out_df = pd.DataFrame(mean_prob, columns=behavior_vals, index=behavior_vals)
    return out_df

def sum_markovs(df_list):
    sum_prob = np.zeros((6,6))
    for df in df_list:
        sum_prob += df.values
    out_df = pd.DataFrame(sum_prob, columns=behavior_vals, index=behavior_vals)
    return out_df

def mean_markovs_new(df_list):
    frequencies = sum_markovs(df_list).values
    normalizing = np.sum(frequencies, axis=-1).reshape(-1,1)
    
    probabilities = (frequencies)/normalizing
    probabilities = np.nan_to_num(probabilities)
    
    return  pd.DataFrame(probabilities, index=behavior_vals, columns=behavior_vals)
    
        

def main():
    get_jaaba_features("trx.mat")
    
if __name__ == "__main__":
    main()