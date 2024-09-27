import os
from random import randint
from flask import request, jsonify
from back_end.views import film_views
from back_end.models.samples.sample_film import SampleFilm
from dotenv import load_dotenv
from back_end.utils.films import (
    MIN_RATING,
    years_in_the_past,
    genres_map,
    get_genres,
    get_movies,
    get_temperature_desc,
)

load_dotenv()


@film_views.route('/by-weather', methods=['GET'])
def get_films_by_weather():
    DEFAULT_TEMPERATURE = 35
    EARLIEST_DATE = years_in_the_past(15)

    API_KEY = os.getenv('TMDB_API_KEY')
    print(f'TMDB_API_KEY: {API_KEY}')  # DEBUG
    if not API_KEY:
        # return films from the sample database
        return jsonify({'error': 'api key missing'}), 401
    try:
        temp_whole = request.args['temperature'].split('.')[0]
        print(f'{temp_whole}')
        temperature = int(temp_whole)
    except AttributeError:
        temperature = DEFAULT_TEMPERATURE

    print(f'Using temperature value: {temperature}')  # DEBUG
    weather = get_temperature_desc(temperature)
    genre_ids = get_genres(weather)

    all_films = {}

    # construct the url parameters
    prefix = 'https://api.themoviedb.org/3/discover/movie?'
    api = f'api_key={API_KEY}'
    genre = 'with_genres={}'
    sort = 'sort_by=popularity.desc'
    vote = f'vote_average.gte={MIN_RATING}'
    date = f'release_date.gte={EARLIEST_DATE}'

    for genre_id in genre_ids:
        url = f"{prefix}&{api}&{vote}&{sort}&{vote}&{date}&" + genre.format(genre_id)
        movies = get_movies(url)
        page_count = int(
            movies['total_pages']
        )  # see how many pages can be returned
        random_page = randint(0, page_count)
        moves = get_movies(
            f"{url}&page={random_page}"
        )  # second request, but from a random page
        for movie in movies['results']:
            movie_id = movie['id']
            if movie_id not in all_films:
                all_films[movie_id] = movie
                break

    return jsonify({'data': all_films}), 200
