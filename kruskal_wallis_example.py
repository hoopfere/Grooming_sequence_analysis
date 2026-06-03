from random import choices
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu 


die = [1, 2, 3, 4, 5, 6]
weights_1 = [1/6] * 6
weights_2 = [0.1, 0.1, 0.1, 0.2, 0.3, 0.2]

results = []
sample_1 = []
sample_2 = []

for i in range(100):
    draw_1 = choices(die, weights_1)[0]
    draw_2 = choices(die, weights_2)[0]
    
    results.append((draw_1, 1))
    results.append((draw_2, 2))
    
    sample_1.append(draw_1)
    sample_2.append(draw_2)
    
    
    
results = np.array(results)

df = pd.DataFrame({"value": results[:, 0], "population": results[:, 1]})

sns.histplot(df, x = "value", hue = "population", discrete = True, multiple = "dodge")
plt.show()

print(mannwhitneyu(sample_1, sample_2, alternative="less"))
    
