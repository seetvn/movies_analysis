import argparse
from utils.dataframe_functions import generate_movies_xlsx, fetch_trends_for_year_grouped,generate_one_hot_encodings_df

# Set up argument parser
parser = argparse.ArgumentParser(description="Script to generate movie trends and encodings.")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
args = parser.parse_args()

# create_exclsx => pytrends to get trends => create hot encodings
if __name__ == "__main__":
    movies_df_without_trends = generate_movies_xlsx(verbose=args.verbose)
    movies_df_with_trends = fetch_trends_for_year_grouped(movies_df_without_trends)
    generate_one_hot_encodings_df(movies_df_with_trends)
    

