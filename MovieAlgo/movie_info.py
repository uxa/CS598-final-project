from config import movie_api_keys
import requests
import random
import re

class MovieInfo:

    def __init__(self):
        self.base_url = 'http://www.omdbapi.com/?apikey={}'.format(random.choice(movie_api_keys))
        self.movie_name_query = 't={}'
        self.movie_year_query = 'y={}'

    def url_join(self, *args):
        return '&'.join([*[self.base_url] + list(args)])

    def perform(self, url, *args):
        return requests.get(url.format(*args))

    def prepare_movie_list(self, movie_year_list):
        '''
        Returns a list request objects containing movie info.
        '''

        final_data = list()
        for movie, year in movie_year_list:
            if ',' in movie:
                movie = movie.split(',')[-1].strip() + ' ' + movie.split(',')[0]
            stats = self.perform(self.url_join(self.movie_name_query, self.movie_year_query), movie, year).json()
            if stats['Response'] == 'True':
                final_data.append(stats)
        
        return final_data

### Helper functions
def get_movie_name_year(movie):
    return [re.split("\(\d+\)", movie)[0].strip(), re.findall("\(\d+\)", movie)[0][1:-1]]
