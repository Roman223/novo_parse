import pandas as pd
import numpy as np

df = pd.read_csv(r"C:\Users\Roman\Desktop\Novo_Parse.csv", sep=';')
df = df[~(df.parsing_date == '08/30/2021, 14:06:00')]
grouped = df[['location', 'parsing_date', 'm2price']].groupby(['location', 'parsing_date']).agg(np.mean)

print('Разница за 31 августа и 1 сентября')
print(pd.DataFrame({'location': grouped.index.get_level_values(level=0)[::2],
                    'diff': [j-i for i, j in zip(grouped['m2price'][::2], grouped['m2price'][1::2])]
                    }))
