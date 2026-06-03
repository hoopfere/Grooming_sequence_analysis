import itertools

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import networkx as nx
import numpy as np
from numpy.__config__ import show
import pandas as pd
import seaborn as sns


class MarkovChain:
    """
    Process and analyze Markov chain data from fly studies
    
    Attributes:
        dfs (list[pd.DataFrame]): Behavioral data from each video. 
        behavior_vals (list[str]): A list of the behaviors in the chain.
        probability_list (list[pd.DataFrame]): Markov probabilities estimated for each chain.
        frequency_list (list[pd.DataFrame]): Frequencies of each transition.
        sequence_list (list[pd.DataFrame]): Sequences of states with current and next state. 
        
        
    """

    def __init__(self, filepath, name=None):
        """
        Initiates a Markov chain, requiring the path of a source .csv and 
        optionally a name for the chain for use in plotting and UI elements

        Arguments:
            filepath (str): the filepath of the .csv containing behavioral data.
            name (str): the name of the treatment group for the .csv.
        """
        
        self.dfs, self.filenames = self._csv_to_dfs(filepath)
        self.behavior_vals: list[str] = sorted(
            list(pd.unique(pd.read_csv(filepath)["behavior"].dropna())) + ["stand"]
        )

        self.behavior_vals.remove("class_all_grooming")

        self.markov_shape = (len(self.behavior_vals), len(self.behavior_vals))

        self.filepath = filepath
        if name is None:
            self.name = filepath.split("/")[-1].split(".")[0]
        else:
            self.name = name

        self._update_chain()
        self._update_entropy()

    def _reorder_behavior_vals(self, new_order: list[str]):
        """
        Changes the order of behavioral states for the chain in place.
        """
        
        self.behavior_vals = new_order
        self._update_chain()

    def _update_chain(self):
        """
        Update values for each of the data lists. Used for UI mostly.
        """
        
        self.markov_shape = (len(self.behavior_vals), len(self.behavior_vals))
        self.probability_list = [self._df_to_markov(df) for df in self.dfs]
        self.frequency_list = [self._df_to_markov(df, counts=True) for df in self.dfs]
        self.sequence_list = [self._df_to_sequence(df) for df in self.dfs]

    def _csv_to_dfs(self, filepath) -> tuple[list[pd.DataFrame], list[str]]:
        """
        Converts an original .csv (from Matlab) into a list of DataFrames for each video in that .csv
        """
        
        data = pd.read_csv(filepath)
        data = data.query("behavior != 'class_all_grooming'")

        dfs = [
            data.query(f"file == '{f}'").sort_values(by="start_time")
            if len(data.query(f"file == '{f}'").sort_values(by="start_time")) > 0 else pd.DataFrame({"file": [f], "behavior": ["stand"], "start_time": [0], "duration": [0]})
            for f in pd.unique(data["file"])]


        filenames = [str(f) for f in pd.unique(data["file"])]

        return dfs, filenames

    def _df_to_markov(self, data, delta=1, counts=False) -> pd.DataFrame:
        """
        given a dataframe with a column "Behavior type", returns a Markov
        chain adjacency matrix representing transitions in that sequence
        """

        behaviors = data["behavior"].tolist()
        start_times = data["start_time"].tolist()
        durations = data["duration"].tolist()

        frequencies = pd.DataFrame(
            np.zeros(self.markov_shape),
            index=pd.Index(self.behavior_vals),
            columns=pd.Index(self.behavior_vals),
        )

        for i in range(len(behaviors) - 1):
            curr = behaviors[i]
            next = behaviors[i + 1]

            if (
                start_times[i + 1] - start_times[i] > durations[i] + delta
                or curr == next
            ):
                frequencies.loc[curr, "stand"] += 1
                frequencies.loc["stand", next] += 1

            else:
                frequencies.loc[next, curr] += 1

        if counts:
            return frequencies

        normalizing = np.sum(frequencies.values, axis=-1).reshape(-1, 1)

        probabilities = (frequencies.values) / normalizing
        probabilities = np.nan_to_num(probabilities)

        markov = pd.DataFrame(
            probabilities,
            index=pd.Index(self.behavior_vals),
            columns=pd.Index(self.behavior_vals),
        )

        return markov

    def _df_to_sequence(self, data, delta=1) -> pd.DataFrame:
        """
        Returns a sequence dataframe with the following features:
            
        Features:
            treatment (str): The treatment
            curr_behavior (str): The current behavior
            next_behavior (str): The next behavior ("last" if last)
            duration (int): The duration of the current behavior
        """
        
        behaviors = data["behavior"].tolist()
        start_times = data["start_time"].tolist()
        durations = data["duration"].tolist()

        sequence = []
        new_durations = []


        for i in range(len(behaviors) - 1):
            curr = behaviors[i]
            sequence.append(curr)
            new_durations.append(durations[i])

            if (
                start_times[i + 1] - start_times[i] - durations[i] > delta
                or curr == next
            ):
                sequence.append("stand")
                new_durations.append(start_times[i + 1] - start_times[i] - durations[i])

        if sequence == []:
            return pd.DataFrame({
                "treatment": [self.name],
                "curr_behavior": ["stand"],
                "next_behavior": ["stand"],
                "duration": [0],
            })
        
        return pd.DataFrame(
            {
                "treatment": [self.name for _ in range(len(sequence))],
                "curr_behavior": sequence,
                "next_behavior": sequence[1:] + ["last"],
                "duration": new_durations,
            }
        )

    def _flatten_df_helper(self, df) -> pd.DataFrame:
        """
        Flattens a Markov matrix dataframe into a single row with columns {source}_{target} for each combination of source and target behavior
        """
        
        wide = (
            df.stack()  # Melt to (row_node, col_node) → value
            .rename_axis(["source", "target"])  # Name the index levels
            .reset_index(name="weight")  # Flatten to a DataFrame
            .assign(
                pair=lambda df: df["source"] + "_" + df["target"]
            )  # Create pair label
            .set_index("pair")[["weight"]]  # Keep only the value column
            .T  # Transpose so pairs become columns
        )

        wide["treatment"] = self.name

        return wide

    def _flattened_df(self) -> pd.DataFrame:
        """
        Flattens multiple dataframes in a list using a helper function
        """
        
        dfs = [self._flatten_df_helper(df) for df in self.probability_list]
        return pd.concat(dfs)

    def sum_markovs(self) -> pd.DataFrame:
        """
        Sums the Markov chain frequencies over all individuals in the population.
        """
        
        sum_prob = np.zeros(self.markov_shape, dtype="float64")
        markovs = self.frequency_list
        for df in markovs:
            sum_prob += df.values
        out_df = pd.DataFrame(
            sum_prob,
            columns=pd.Index(self.behavior_vals),
            index=pd.Index(self.behavior_vals),
        )
        return out_df

    def mean_markovs(self, freq=False):
        """
        Takes the mean over all transition matrices in the population.

        Optionally returns frequencies, rather than probabilities
        """
        
        frequencies = self.sum_markovs().values

        if freq:
            return pd.DataFrame(
                frequencies,
                index=pd.Index(self.behavior_vals),
                columns=pd.Index(self.behavior_vals),
            )
        normalizing = np.sum(frequencies, axis=-1).reshape(-1, 1)

        probabilities = (frequencies) / normalizing
        probabilities = np.nan_to_num(probabilities)

        return pd.DataFrame(
            probabilities,
            index=pd.Index(self.behavior_vals),
            columns=pd.Index(self.behavior_vals),
        )

    def get_interbout(self) -> list[int]:
        """
        Gets the interbout durations over the entire population. Useful for determining a non-grooming delta for analysis.
        """
        
        breaks = []

        for data in self.dfs:
            start_times = data["start_time"].tolist()
            durations = data["duration"].tolist()

            for i in range(len(start_times) - 1):
                breaks.append(start_times[i + 1] - start_times[i] - durations[i])

        return breaks

    def show_markov_heatmap(self, show_stand=True) -> Axes:
        """
        Returns a Matplotlib Axes object that is a heatmap of the transition probabilities for the population.
        """
        
        plt.close()
        if show_stand:
            p = sns.heatmap(self.mean_markovs())
        else:
            p = sns.heatmap(
                self.mean_markovs().drop("stand", axis=1).drop("stand", axis=0)
            )
        return p

    def show_markov_graph(self, hide_stand=False, title="Markov Chain Graph"):
        """
        Displays a NetworkX graph of the transition matrices over the population
        """
        
        data = self.mean_markovs()
        if hide_stand:
            data = data.drop("stand", axis=1).drop("stand", axis=0)

        threshold = 0.05
        width_scale = 20  # controls visual thickness

        # Build directed graph with a stable node order
        G = nx.DiGraph()
        node_order = [state for state in self.behavior_vals if state in data.index]

        G.add_nodes_from(node_order)

        for from_state in node_order:
            for to_state in node_order:
                prob = data.loc[from_state, to_state]
                if prob > threshold:
                    G.add_edge(from_state, to_state, weight=prob)

        # Layout
        pos = nx.circular_layout(G)

        plt.figure(figsize=(16, 8))

        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos, node_size=3000, node_color="lightblue", edgecolors="black"
        )

        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=12)

        # Edge widths proportional to transition probability
        edge_widths = [width_scale * d["weight"] for _, _, d in G.edges(data=True)]

        # Draw edges
        nx.draw_networkx_edges(
            G,
            pos,
            width=edge_widths,
            arrowstyle="->",
            arrowsize=20,
            node_size=4000,
            connectionstyle="arc3,rad=0.2",
        )

        # Edge labels
        edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}

        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_size=10, label_pos=0.6
        )

        plt.title(title)
        plt.axis("off")
        plt.show()

    def _update_entropy(self):
        """
        Markov chain entropy calculation from "Estimating the Entropy Rate of Finite Markov Chains With Application to Behavior Studies" (2019)
        """
        
        entropy_vals = []

        for i in range(len(self.probability_list)):
            markov = self.probability_list[i]
            counts = self.frequency_list[i]

            with np.errstate(divide="ignore"):
                state_entropy = -np.sum(
                    markov * np.nan_to_num(np.log(markov), nan=0), axis=1
                )
            stationary_dist = counts.sum(axis=0) / counts.sum()

            entropy = (stationary_dist * state_entropy).sum()

            entropy_vals.append(entropy)

        self.entropy_vals, self.mean_entropy, self.std_entropy = (
            entropy_vals,
            np.mean(entropy_vals),
            np.std(entropy_vals),
        )

    def get_best_ordering(self) -> None:
        """
        The idea here is to get the best ordering of transtion states
        based on the number of ordinal skips that the transitions have to make.
        """
        # TODO: finish this functionality
        for ordering in itertools.permutations(self.behavior_vals):
            skip_sum = 0
            for sequence in self.sequence_list:
                skip_sum += self.get_num_skips(sequence, ordering)

            print(ordering, skip_sum)
            
        pass

    def get_num_skips(self, sequence, ordering) -> int:
        """
        Helper function for get_best_ordering
        """
        skip_count = 0
        for i in range(len(sequence) - 1):
            from_state = sequence[i]
            to_state = sequence[i + 1]

            from_idx = ordering.index(from_state)
            to_idx = ordering.index(to_state)

            skip_count += abs(from_idx - to_idx)
        return skip_count

    def export_summary(self):
        """
        Returns a summary DataFrame containing treatment, filename, and entropy for each individual in the population.
        """
        # TODO: add flattened representation of Markov chain
        
        data = {
            "treatment": [self.name for _ in range(len(self.filenames))],
            "filenames": self.filenames,
            "entropies": self.entropy_vals,
        }

        return pd.DataFrame.from_dict(data)


    
        
