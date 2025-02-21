import argparse
from utils.dataframe_functions import generate_movies_xlsx, fetch_trends_for_year_grouped,generate_one_hot_encodings_df
from utils.file_paths import get_file_paths

# Set up argument parser
parser = argparse.ArgumentParser(description="Script to generate movie trends and encodings.")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
args = parser.parse_args()

# Get file paths
file_paths = get_file_paths()

# create_exclsx => pytrends to get trends => create hot encodings
if __name__ == "__main__":
    # creates df without search trends
    movies_df_without_trends = generate_movies_xlsx(verbose=args.verbose)

    # adds search trend later on with pytrend
    movies_df_with_trends = fetch_trends_for_year_grouped(movies_df_without_trends,file_name="movies_formatted.xlsx",file_path=file_paths['formatted'])
    
    # creates hot encoding
    hot_encodings_df = generate_one_hot_encodings_df(movies_df_with_trends,file_name="movies_one_hot_encodings.xlsx",file_path=file_paths['formatted'])

    # save in backupdata
    movies_df_with_trends.to_excel(file_paths['backup_formatted'] + 'movies_formatted.xlsx')
    hot_encodings_df.to_excel(file_paths['backup_formatted'] + 'movies_one_hot_encodings.xlsx')
    
