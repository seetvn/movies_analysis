import pandas as pd
from dataframe_functions import generate_movies_xlsx
# data = pd.read_excel("/home/seetvn/random_projects/ekimetrics/data/movies_str.xlsx")

# data = format_df(data,verbose=True)
# print('===== step1: done ====== \n')
# data = drop_invalid_NaN_boxoffice_values(data,verbose=True)
# print('==== step2: done ====== \n')
# indices = data[data['BoxOffice'].isna()].index
# data = refactor_valid_NaN_boxoffice_values(data,verbose=True)
# print(data.loc[indices])
# print('==== step3: done ====== \n')

df = generate_movies_xlsx(verbose=True)

print(df.head())