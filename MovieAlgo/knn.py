import pandas as pd
import numpy as np
import pickle
import os

curr_path = os.path.dirname(__file__)

class KNN:

    def __init__(self):
        self.movies = pd.read_csv(os.path.join(curr_path, 'data/movies-dat.csv'))
        self.ratings = pd.read_csv(os.path.join(curr_path, 'data/ratings-dat.csv'))
        with open(os.path.join(curr_path,'data/knn.pkl'), 'rb') as f:
            self.model = pickle.load(f)


    def predict(self, data):
        data_matrix = np.zeros(shape = (1, 3706))

        for item in data:
            data_matrix[0, int(item['movie_id']) - 1] = float(item['rating'])

        return self.get_top_movies(self.model.kneighbors(data_matrix)[1][0], self.movies, self.ratings)

    def get_top_movies(self, users, movies, ratings):
    
        movie_user_rating = movies
        movie_user_rating = movie_user_rating.drop(['genre 1', 'genre 2','genre 3','genre 4','genre 5','genre 6',], axis=1)
        movie_user_rating = movie_user_rating.set_index('movie_id')
        movie_user_rating['size'] = 0
        movie_user_rating['rating_total'] = 0
        
        for user in users:
            user_ratings = ratings[ratings['user_id'] == user  - 1]
            for index, row in user_ratings.iterrows():
                movie_id = row['movie_id']
                rating_user = row['rating']
                movie_user_rating.loc[movie_id,'rating_total'] = movie_user_rating.loc[movie_id,'rating_total'] + rating_user
                movie_user_rating.loc[movie_id,'size'] = movie_user_rating.loc[movie_id,'size'] + 1
        
        movie_user_rating = movie_user_rating[movie_user_rating['size'] !=0]
        movie_user_rating['mean_rating']  = movie_user_rating['rating_total'] / movie_user_rating['size']
        movie_user_rating = movie_user_rating.sort_values(by=['mean_rating','size'], ascending=False)
        top_movies = movie_user_rating['movie'].tolist()
        return top_movies