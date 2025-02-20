from api_calls.omdb_api import call_ombd_api,get_relevant_attributes
from pytrends.request import TrendReq
import pandas as pd
import time
import random
from typing import Union,List

# Initialize Pytrends
pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25), retries=3, backoff_factor=0.1)

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
    df.to_excel("/home/seetvn/random_projects/ekimetrics/data/unformatted/movies_unformatted.xlsx",index=False)
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
    # + replace Not Rated with Unrated
    dataframe["Rated"] = dataframe["Rated"].replace("Not Rated","Unrated")
    
    if verbose:
        print("The columns: 'imdbVotes' , 'BoxOffice', 'Runtime', 'Rated' have been formatted \n")

    return dataframe

def drop_invalid_NaN_boxoffice_values(dataframe: pd.DataFrame,verbose=False)-> pd.DataFrame:
    """
    drops invalid NaN boxoffice values if they are TV shows or less than 10000 imdb votes
    """
    # get rid of (NaN BoxOffice and NaN rated), (NaN BoxOffice, imdbVotes < 10000), (NaN BoxOffice, TV rating)
    prev_shape = dataframe.shape[0] if verbose else None
    dataframe = dataframe.drop(dataframe[(dataframe["BoxOffice"].isna()) & (dataframe["imdbVotes"] < 10000)].index)
    dataframe = dataframe.drop(dataframe[(dataframe["BoxOffice"].isna()) & (dataframe["Rated"].isin(['TV-14', 'TV-MA', 'TV-PG']))].index)
    dataframe = dataframe.drop(dataframe[(dataframe["BoxOffice"].isna()) & (dataframe["Rated"].isna())].index)

    if verbose:
        current_shape = dataframe.shape[0]
        print(f"The dataframe previously had {prev_shape} rows and now has {current_shape} rows after dropping invalid NaN boxoffice rows \n")
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
    
def generate_movies_xlsx(verbose=False) -> pd.DataFrame:
    final_file_path = '/home/seetvn/random_projects/ekimetrics/data/formatted/movies_formatted.xlsx'

    # retrieve as text data into xlsx
    data = generate_movies_xlsx_str(verbose=verbose)
    if verbose:
        print(" STEP 1: === excel with text values have been generated === \n\n")
    
    # format to turn into numerical data
    data = format_df(data,verbose=verbose)
    if verbose:
        print(" STEP 2: ===  text values have been formatted into numerical data  ===\n\n")

    # drop NaN values
    data = drop_invalid_NaN_boxoffice_values(data,verbose=verbose)
    if verbose:
        print(" STEP 3: ===  Invalid NaN values dropped  === \n\n")

    # refactor valid NaN values
    data = refactor_valid_NaN_boxoffice_values(data,verbose=verbose)
    if verbose:
        print(" STEP 4: ===  Valid NaN values refactored  ===\n\n")
    
    # turn into xlsx
    data.to_excel(final_file_path,index=False)
    print(" === NEW EXCEL FILE GENERATED ===")
    return data

def generate_one_hot_encodings_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    creates one hot encoding df
    meant for genre and rated analysis
    """
    # Genre
    genre_df_encoded = dataframe["Genre"].str.get_dummies(sep=", ")
    dataframe["Rated"] = dataframe["Rated"].fillna("Unrated")
    # unique rated values
    unique_rated_values = dataframe["Rated"].unique()
    # Create a new DataFrame for one-hot encoding for rated
    ratings_one_hot_df = pd.DataFrame(index=dataframe.index)
    # Populate the new DataFrame with one-hot encoded columns
    for rated_value in unique_rated_values:
        ratings_one_hot_df[rated_value] = (dataframe["Rated"] == rated_value).astype(int)
    one_hot_encodings_df = pd.concat([dataframe['Title'],genre_df_encoded,dataframe['imdbRating'],dataframe['BoxOffice'],dataframe['Search Trend'],dataframe['Year'],ratings_one_hot_df],axis=1)
    one_hot_encodings_df.to_excel("/home/seetvn/random_projects/ekimetrics/data/formatted/movies_one_hot_encodings.xlsx",index=False)

    return one_hot_encodings_df


def fetch_trends_for_year_grouped(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fetches the trend for each film relative
    to the rest that were released in the same year
    """
    movie_popularity = {}
    movie_list = regroup_for_pytrends(df)
    for year, movies in movie_list:
        print(year, movies)
        # Skip years before 2009
        if year < 2009:
            print(f"Skipping {year} (Google Trends does not support years before 2009)")
            for movie in movies:
                movie_popularity[movie] = None
            continue
        timeframe = get_one_year_timeframe(year)
        try:
            pytrends.build_payload(movies, timeframe=timeframe)
            trend_data = pytrends.interest_over_time()
            if not trend_data.empty:
                for movie in movies:
                    movie_popularity[movie] = trend_data[movie].sum()
            else:
                for movie in movies:
                    movie_popularity[movie] = None
            # Introduce a random delay to avoid Google blocking requests
            time.sleep(random.uniform(20, 30))
        except Exception as e:
            print(f"Error fetching trends for {year}: {e}")
            for movie in movies:
                movie_popularity[movie] = None

    # Add the search interest to the original DataFrame
    df["Search Trend"] = df["Title"].map(movie_popularity)
    df.to_excel("/home/seetvn/random_projects/ekimetrics/data/formatted/movies_formatted.xlsx",index=False)
    return df

# HELPER Functions
def regroup_for_pytrends(df: pd.DataFrame)-> List:
    """
    Breaks down big lists of movies into smaller
    chunks of max length 3 to allow PyTrend to
    return less errors
    """

    # Group movies by release year
    grouped_movies = df.groupby("Year")["Title"].apply(list)
    new_list = []
    for movie_info in grouped_movies.items():
        new_list.extend(split_into_threes(movie_info))
    return new_list

# HELPER FUNCTIONS
def split_into_threes(movies_list) -> List:
    final_list = []
    new_list = []
    year = movies_list[0]
    for movie in movies_list[1]:
        # print(movie)
        new_list.append(movie)
        if len(new_list) == 3:
            final_list.append([year,new_list])
            new_list = []
    if new_list:
        final_list.append([year,new_list])
    return final_list

# HELPER FUNCTIONS
def get_one_year_timeframe(release_year: str) -> str:
    """
    Generate a 1-year timeframe for Google Trends
    """
    start_date = f"{release_year}-01-01"
    end_date = f"{int(release_year) + 1}-01-01"
    return f"{start_date} {end_date}"