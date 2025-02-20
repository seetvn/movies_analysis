import pandas as pd
from dataframe_functions import generate_one_hot_encodings_df
df = pd.read_excel("/home/seetvn/random_projects/ekimetrics/data/formatted/movies_formatted.xlsx")
print(df.columns)

# print(df.head(12))
# print(df.loc[((df['Search Trend'].isna() != True) & (df['Year']==2010)),['Title','imdbRating','BoxOffice','Search Trend']])

df = generate_one_hot_encodings_df(df)
print(df.head(9))

