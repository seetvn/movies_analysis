import requests
from typing import Dict, Any,Union,List
import os

# hardcoded in
API_KEY = "8b0e8f6a"
print(API_KEY)

relevant_attributes = ['Title','Year','Rated','imdbVotes','imdbRating','Runtime', 'Genre', 'BoxOffice']

def call_ombd_api(movie_name: str) -> Union[Dict[str,Any], List[str]]:
    api_url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={movie_name}"
    response = requests.get(api_url)
    # Convert response to JSON
    data = response.json()
    return data,data.keys()

def get_relevant_attributes() -> List[str]:
    return relevant_attributes

if __name__ == "__main__":
    data,keys = call_ombd_api("Sausage Party")
    print(data)
    print(keys)

