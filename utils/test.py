import pandas as pd
from dataframe_functions import generate_genre_one_hot_encodings_df
df = pd.read_excel("/home/seetvn/random_projects/ekimetrics/data/formatted/movies_formatted.xlsx")

df = generate_genre_one_hot_encodings_df(df)
print(df.loc[11])