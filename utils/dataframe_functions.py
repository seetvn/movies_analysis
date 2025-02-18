from api_calls.omdb_api import call_ombd_api,get_relevant_attributes
import pandas as pd
from typing import Union
#TODO: add more films to movies.xlsx
def generate_movies_xlsx_str(verbose=False) -> Union[pd.DataFrame,pd.DataFrame]:
    data = pd.read_excel('/home/seetvn/random_projects/ekimetrics/data/movies.xlsx')
    xlsx_dict = {'Title':[],'Year':[],'Rated':[],'imdbVotes':[],'imdbRating':[],'Runtime':[], 'Genre':[], 'BoxOffice':[]}
    relevant_attributes = get_relevant_attributes()
    for index, row in data.iterrows():
        movie_title = row['title']
        if verbose:
            print(f"{index} film: {movie_title}")
        movie_info,_ = call_ombd_api(movie_title)
        for relevant_attribute in relevant_attributes:
            xlsx_dict[relevant_attribute].append(movie_info[relevant_attribute])
    df = pd.DataFrame(xlsx_dict)
    df.to_excel("/home/seetvn/random_projects/ekimetrics/data/movies_unformatted.xlsx",index=False)
    return df

def format_df(dataframe: pd.DataFrame,verbose=False) ->pd.DataFrame:
    """
    refactors these fields into numerical data
    """
    # refactor imdbVotes
    dataframe["imdbVotes"] = pd.to_numeric(dataframe["imdbVotes"].str.replace(",", ""), errors="coerce")
    # refactor BoxOffice
    dataframe["BoxOffice"] = pd.to_numeric(dataframe["BoxOffice"].str.replace("[$,]","",regex=True), errors="coerce")
    # refactor Runtime
    dataframe["Runtime"] = pd.to_numeric(dataframe["Runtime"].str.replace("min",""), errors="coerce")

    if verbose:
        print("The columns: 'imdbVotes' , 'BoxOffice', 'Runtime' has been formatted correctly")

    return dataframe

def drop_invalid_NaN_boxoffice_values(dataframe: pd.DataFrame,verbose=False)-> pd.DataFrame:
    """
    drops invalid NaN boxoffice values if they are TV shows or less than 10000 imdb votes
    """
    # TODO: below
    # get rid of (NaN BoxOffice and NaN rated), (NaN BoxOffice, imdbVotes < 10000), (NaN BoxOffice, TV rating)
    prev_shape = dataframe.shape[0] if verbose else None
    dataframe =   dataframe.drop(dataframe[(dataframe["BoxOffice"].isna()) & (dataframe["imdbVotes"] < 10000)].index)
    dataframe = dataframe.drop(dataframe[(dataframe["BoxOffice"].isna()) & (dataframe["Rated"].isin(['TV-14', 'TV-MA', 'TV-PG']))].index)
    dataframe = dataframe.drop(dataframe[(dataframe["BoxOffice"].isna()) & (dataframe["Rated"].isna())].index)

    if verbose:
        current_shape = dataframe.shape[0]
        print(f" The dataframe previously had {prev_shape} rows and now has {current_shape} rows after dropping invalid NaN boxoffice rows")
    return dataframe

def refactor_valid_NaN_boxoffice_values(dataframe: pd.DataFrame,verbose=False)-> pd.DataFrame:
    """
    replaces the remaining Nan boxoffice values with 
    the mean value of the boxoffice of the corresponding
    rated value
    """
    different_rated_values = dataframe[dataframe["BoxOffice"].isna()]["Rated"].unique()
    for rated_value in different_rated_values:
            mean_value = dataframe[dataframe["Rated"] == rated_value]["BoxOffice"].mean()
            dataframe.loc[(dataframe["Rated"] == rated_value) & (dataframe["BoxOffice"].isna()), "BoxOffice"] = mean_value
    return dataframe
    

# my_df = generate_movies_xlsx_str(verbose=True)
# print(my_df.head())