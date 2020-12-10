from flask import Flask, render_template, flash, request, redirect, url_for
from flask_cors import CORS
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_wtf.recaptcha import RecaptchaField, Recaptcha
from flask_wtf.csrf import CSRFProtect
from wtforms import TextField, TextAreaField, StringField, SubmitField, SelectField, IntegerField, FieldList, FormField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms import validators
import pandas as pd
from math import ceil
import json

from MovieAlgo.movie_info import MovieInfo, get_movie_name_year
from MovieAlgo.knn import KNN

'''
CS 598 - Practical Statistical Learning Project 3
UIUC, Fall 2020

@authors:
- Pranav Velamakanni (pranavv2@illinois.edu)
- Tarik Koric (koric1@illinois.edu)
'''

# App config.
app = Flask(__name__)
CORS(app)
CSRFProtect(app)
Bootstrap(app)
app.config.from_object(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# Load metadata
with open('data/movie_data.json') as f:
    movie_names_id = json.loads(f.read())

# Pre-load model and data for System 2
model = KNN()

class MovieRecommendation1(FlaskForm):

    genre_coices = sorted(['Animation',
                    'Romance',
                    'Action',
                    'Crime',
                    'Film-Noir',
                    'War',
                    'Fantasy',
                    'Drama',
                    'Musical',
                    'Comedy',
                    'Mystery',
                    'Documentary',
                    'Thriller',
                    'Western',
                    'Adventure',
                    'Horror',
                    "Children's",
                    'Sci-Fi'])
    
    algo_choice = ['Number of reviews', 'Mean rating', 'Weighted rating']

    genre = SelectField('Genre', choices = genre_coices, description = "Pick a genre to receive recommendations for.", validators = [DataRequired()])
    algo = SelectField('Rated by', choices = algo_choice, description = "Pick a rating algorithm.", validators = [DataRequired()])
    number = IntegerField('Recommendations',  default = 5, description = "Number of recommendations, limited to 20.", validators = [DataRequired(), NumberRange(min=1, max=20, message = 'Must be within 1 and 20, default is 5.')])

    submit = SubmitField()

@app.route('/', methods = ('GET', 'POST'))
def index():

    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('confused.html'), 404

@app.route('/system1', methods = ('GET', 'POST'))
def system1():
    '''
    Serves the /system1 end point. Redirects to /results for POST.
    '''
    form = MovieRecommendation1()
    if request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for('results1', genre = request.form.get('genre'), algo = request.form.get('algo'), number = request.form.get('number')))

    return render_template('system1.html', form = form)

@app.route('/results/<genre>/<algo>/<number>', methods = ['GET'])
def results1(genre, algo, number):
    '''
    Processes requests for System 1. 
    NOTE: This end point is not intended to be used like an API to avoid maxing out resource limits.
    '''

    #if not request.referrer:
    #    return render_template('confused.html'), 401

    #####
    ## Movie analysis - System 1
    #####

    algo_map = {'Number of reviews': 'size', 'Mean rating': 'mean_ratings', 'Weighted rating': 'weighted_rating'}

    data = pd.read_csv('data/final_ratings.csv')
    results = data[(data['genre 1']  == genre) | (data['genre 2'] == genre) | (data['genre 3'] == genre) | (data['genre 4'] == genre) | (data['genre 5'] == genre) | (data['genre 6'] == genre)].sort_values(by=[algo_map.get(algo)], ascending=False).head(int(number))
    movie_year_list = [*map(get_movie_name_year, list(results.movie))]

    MovieStats = MovieInfo()
    final_data = MovieStats.prepare_movie_list(movie_year_list)

    return render_template('success.html', data = final_data)

class MovieForm(FlaskForm):

    movie_name = SelectField(
        'Movie',
        description = 'Pick a movie to rate',
        choices = sorted(movie_names_id.keys()),
        validators = [DataRequired()]
    )

    rating = FloatField(
        'Rating',
        description = 'Rate the movie from 1.0 to 5.0',
        validators=[NumberRange(min = 1.0, max = 5.0, message='Value must be between 1 and 5')]
    )

class System2(FlaskForm):
    '''
    System 2 parent form.
    '''

    movies = FieldList(
        FormField(MovieForm),
        min_entries=1,
        max_entries=10
    )

    number = IntegerField(
        'Recommendations',
        default = 5,
        description = "Number of recommendations to display, limited to 20.",
        validators = [NumberRange(min=1, max=20, message = 'Must be within 1 and 20, default is 5.')]
    )

class RequestFormResponse2:

    def __init__(self, form):
        self.raw_data = form
        self.recommendations = int(form['number'])
        self.form_data = self.prepare_data(form)

    def prepare_data(self, data):
        final_data = list()
        for i in range(ceil((len(data) - 3) / 2)):
            temp = dict()
            temp['movie_name'] = data['movies-{}-movie_name'.format(i)]
            temp['movie_id'] = movie_names_id.get(temp['movie_name'])
            temp['rating'] = data['movies-{}-rating'.format(i)]
            final_data.append(temp)
        return final_data

@app.route('/system2', methods=['POST', 'GET'])
def system2():

    form = System2()
    template_form = MovieForm(prefix='movies-_-')

    if request.method == 'POST':
        if form.validate_on_submit():
            data = RequestFormResponse2(request.form)
            results = model.predict(data.form_data)
            movie_year_list = [*map(get_movie_name_year, results[:data.recommendations])]

            MovieStats = MovieInfo()
            final_data = MovieStats.prepare_movie_list(movie_year_list)

            return render_template('success.html', data = final_data)
 
    return render_template('system2.html', form=form, _template = template_form)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', threaded = True, port = 5000)
