import pandas as pd
from dataframe_functions import generate_movies_xlsx
df = pd.read_excel("/home/seetvn/random_projects/ekimetrics/data/movies_formatted.xlsx")
print(df.dtypes)
print(df['Genre'].unique)
