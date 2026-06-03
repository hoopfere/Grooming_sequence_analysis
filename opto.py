import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd
    from MarkovChain import MarkovChain

    return MarkovChain, mo, pd


@app.cell
def _(pd):
    data = {"opto": pd.read_csv("data/grooming_opto.csv"), "non_opto": pd.read_csv("data/non_grooming_opto.csv")}
    return (data,)


@app.cell
def _(data):
    bounds = {f"{40*chunk}_{40*(chunk + 1) - 10}":(40*chunk, (40*(chunk + 1)) - 10) for chunk in range(4)}

    chunked = [{f"opto_data/{name}_{chunk}.csv": data[name].query("start_time >= @bounds[@chunk][0] and start_time < @bounds[@chunk][1]").to_csv(f"opto_data/{name}_{chunk}.csv") for chunk in bounds} for name in data]
    return (chunked,)


@app.cell
def _(chunked):
    chunked
    return


@app.cell
def _(MarkovChain, chunked):
    opto = [MarkovChain(filepath=i) for i in chunked[0]]
    non_opto = [MarkovChain(filepath=i) for i in chunked[1]]

    for i in range(4):
        opto[i]._reorder_behavior_vals(['abdominal', 'back_leg_rubbing', 'front_leg_rubbing', 'head', 'stand', 'thorax', 'wing'])
        non_opto[i]._reorder_behavior_vals(['abdominal', 'back_leg_rubbing', 'front_leg_rubbing', 'head', 'stand', 'thorax', 'wing'])
    return non_opto, opto


@app.cell
def _(mo, non_opto, opto):
    mo.vstack([mo.hstack([mo.vstack([chunk.show_markov_heatmap(), chunk.name, f'entropy: {chunk.mean_entropy}', f'n: {len(chunk.dfs)}']) for chunk in frame]) for frame in [opto, non_opto]])
    return


if __name__ == "__main__":
    app.run()
