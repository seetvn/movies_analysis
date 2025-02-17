import pandas as pd
data = pd.read_excel("../data/movies.xlsx")

print(data['title'][120:135])

