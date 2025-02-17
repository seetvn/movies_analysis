from api_calls.omdb_api import call_ombd_api,get_relevant_attributes
import pandas as pd

def generate_movies_xlsx():
    data = pd.read_excel('/home/seetvn/random_projects/ekimetrics/data/movies.xlsx')
    xlsx_dict = {'Title':[],'Year':[],'Rated':[],'imdbVotes':[],'imdbRating':[],'Runtime':[], 'Genre':[], 'BoxOffice':[]}
    relevant_attributes = get_relevant_attributes()
    for index, row in data[1:5].iterrows():
        movie_title = row['title']
        movie_info,_ = call_ombd_api(movie_title)
        for relevant_attribute in relevant_attributes:
            xlsx_dict[relevant_attribute].append(movie_info[relevant_attribute])
    df = pd.DataFrame(xlsx_dict)
    df.to_excel("/home/seetvn/random_projects/ekimetrics/data/movies_with_attributes.xlsx",index=False)
    return df

my_df = generate_movies_xlsx()
print(my_df.head())