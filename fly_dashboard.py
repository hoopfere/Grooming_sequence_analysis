import marimo

__generated_with = "0.23.4"
app = marimo.App(width="full", app_title="Fly Dashboard")


@app.cell(hide_code=True)
def _(
    chain1,
    chain2,
    embedding_radio,
    entropy_test,
    mo,
    plot_embeddings,
    plot_entropy,
    plot_markovs,
    test_radio,
):
    chart = plot_embeddings(method=embedding_radio.value)
    entropy_test_result = entropy_test(chain1.entropy_vals, chain2.entropy_vals, test_type=test_radio.value)

    mo.vstack([plot_markovs(), mo.hstack([plot_entropy(), chart], widths="equal")])

    return chart, entropy_test_result


@app.cell(hide_code=True)
def _(
    chain1,
    chain2,
    choose_behavior,
    ds_dd1,
    ds_dd2,
    ds_label1,
    ds_label2,
    embedding_radio,
    entropy_test_result,
    mo,
    pd,
    test_radio,
):
    mo.vstack(
        [
            mo.hstack([
                mo.vstack([ds_dd1, ds_dd2,
                pd.concat([chain1.export_summary(), chain2.export_summary()])
            ]),
            mo.vstack([ds_label1, ds_label2]), embedding_radio, choose_behavior])
        ]
    )

    mo.vstack([
        mo.hstack([mo.vstack([mo.hstack([mo.vstack([mo.hstack([ds_dd1, ds_dd2, embedding_radio]), mo.hstack([ds_label1, ds_label2, test_radio, mo.md(f'''P-value:
        {entropy_test_result[1]}''')]), choose_behavior])])]), pd.concat([chain1.export_summary(), chain2.export_summary()])])
    ])
    return


@app.cell
def _(markov_fig):
    markov_fig
    return


@app.cell(hide_code=True)
def _(
    PCA,
    TSNE,
    alt,
    chain1,
    chain2,
    choose_behavior,
    kruskal,
    mo,
    np,
    pd,
    plt,
    sns,
    ttest_ind,
):
    mo.stop(chain1.behavior_vals != chain2.behavior_vals, output="The selected chains do not have the same behaviors")

    chain1._reorder_behavior_vals(new_order=choose_behavior.value["value"])
    chain2._reorder_behavior_vals(new_order=choose_behavior.value["value"])

    def plot_markovs():

        fig, axes = plt.subplots(1, 3, figsize=(30, 7), sharex=True)

        sns.heatmap(
            chain1.mean_markovs(), ax=axes[0], vmin=0, vmax=1, cmap="coolwarm"
        )
        axes[0].set_title(chain1.name)

        sns.heatmap(
            chain2.mean_markovs(), ax=axes[1], vmin=0, vmax=1, cmap="coolwarm"
        )
        axes[1].set_title(chain2.name)

        sns.heatmap(
            chain1.mean_markovs() - chain2.mean_markovs(),
            ax=axes[2],
            cmap="coolwarm",
        )
        axes[2].set_title(format(f"Difference: {chain1.name} - {chain2.name}"))

        return fig

    def plot_entropy():
        chain1_list = chain1.entropy_vals
        chain2_list = chain2.entropy_vals

        fig = plt.figure()

        sns.kdeplot(
            pd.DataFrame(
                {
                    "Entropy": chain1_list + chain2_list,
                    "Treatment": [chain1.name] * len(chain1_list)
                    + [chain2.name] * len(chain2_list),
                }
            ),
            x="Entropy",
            hue="Treatment",
            fill=True,
        )

        return fig

    def scatter(df):
        return (
            alt.Chart(df)
            .mark_circle()
            .encode(x=alt.X("x:Q"), y=alt.Y("y:Q"), color=alt.Color("treatment:N"))
        )

    def plot_embeddings(method="PCA", freq=False):
        if method == "PCA":
            embedder = PCA(n_components=2)
        else:
            embedder = TSNE(
                n_components=2,
                init="random",
                max_iter=1000,
                random_state=1,
            )

        X = np.array(
            [
                np.reshape(df.values, len(chain1.behavior_vals) ** 2)
                for df in chain1.frequency_list + chain2.frequency_list
            ]
            if freq
            else [
                np.reshape(df.values, len(chain1.behavior_vals) ** 2)
                for df in chain1.probability_list + chain2.probability_list
            ]
        )

        Y = embedder.fit_transform(X)

        treatment = [chain1.name] * len(chain1.probability_list) + [chain2.name] * len(
            chain2.probability_list
        )

        embedding = pd.DataFrame({"treatment": treatment, "x": Y[:, 0], "y": Y[:, 1]})

        chart = mo.ui.altair_chart(scatter(embedding))

        return chart

    def entropy_test(chain1, chain2, test_type = "KW Test"):
        if test_type == "KW Test":
            stat, p_value = kruskal(chain1, chain2)
        else:
            stat, p_value = ttest_ind(chain1, chain2)

        return stat, p_value



    return entropy_test, plot_embeddings, plot_entropy, plot_markovs


@app.cell(hide_code=True)
def _(chain1, chart, mo, selected_markov, selected_markov_plot):
    if len(chart.value) == 0:
        markov_fig = "Markov chain not selected"

    else:
        markov_fig = mo.hstack([mo.ui.matplotlib(selected_markov_plot), mo.ui.table(selected_markov, format_mapping={
            i: "{:.2f}".format for i in chain1.behavior_vals  # Formats to 2 decimal places
        }
    )])
    return (markov_fig,)


@app.cell(hide_code=True)
def _(chain1, chain2, chart, plt, sns):
    # mo.stop(len(chart.value) == 0)

    plt.figure(figsize=(3, 3))

    if len(chart.value != 0):
        selected_markov = (chain1.probability_list + chain2.probability_list)[chart.value.index[0]]
    else:
        selected_markov = (chain1.probability_list + chain2.probability_list)[0]

    selected_markov_plot = sns.heatmap(
        selected_markov,
        vmin=0,
        vmax=1,
        cmap="coolwarm",
        square=True,
    )
    return selected_markov, selected_markov_plot


@app.cell(hide_code=True)
def _(mo, os):
    options = sorted(os.listdir("data/"))

    ds_dd1 = mo.ui.dropdown(options=options, label="choose dataset 1", value=options[4])
    ds_label1 = mo.ui.text(label="dataset 1 name:", value="chain1")
    ds_dd2 = mo.ui.dropdown(options=options, label="choose dataset 2", value=options[7])
    ds_label2 = mo.ui.text(label="dataset 2 name:", value="chain2")
    embedding_radio = mo.ui.radio(options=["PCA", "t-SNE"], value="PCA")
    test_radio = mo.ui.radio(options=["T-Test", "KW Test"], value="T-Test")
    return ds_dd1, ds_dd2, ds_label1, ds_label2, embedding_radio, test_radio


@app.cell(hide_code=True)
def _(MarkovChain, SortableList, ds_dd1, ds_dd2, ds_label1, ds_label2, mo):
    chain1 = MarkovChain(filepath="data/" + ds_dd1.value, name=ds_label1.value)
    chain2 = MarkovChain(filepath="data/" + ds_dd2.value, name=ds_label2.value)


    choose_behavior = mo.ui.anywidget(
        SortableList(
            value=chain1.behavior_vals, editable=True, label="Behavioral Order"
        )
    )
    return chain1, chain2, choose_behavior


@app.cell(hide_code=True)
def _():
    import os

    import altair as alt
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns

    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from scipy.stats import kruskal
    from scipy.stats import ttest_ind

    from wigglystuff import SortableList

    from MarkovChain import MarkovChain

    return (
        MarkovChain,
        PCA,
        SortableList,
        TSNE,
        alt,
        kruskal,
        mo,
        np,
        os,
        pd,
        plt,
        sns,
        ttest_ind,
    )


if __name__ == "__main__":
    app.run()
