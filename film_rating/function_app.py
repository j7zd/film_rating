import azure.functions as func
import datetime as dt
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

engine = create_engine('mysql+pymysql://root:root@localhost:3306/db')
Session = sessionmaker(bind=engine)

app = func.FunctionApp()

@app.route(route="film", methods=["POST", "GET"], auth_level=func.AuthLevel.FUNCTION)
def film(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "GET":
        search = req.params.get('search')

        if search:
            session = Session()
            films = session.query(models.Film).filter(models.Film.title.ilike(f"%{search}%")).all()
            session.close()
        else:
            session = Session()
            films = session.query(models.Film).all()
            session.close()

        film_data = []
        for film in films:
            ratings = session.query(models.Rating).filter(models.Rating.film_id == film.id).all()
            ratings_data = []
            for rating in ratings:
                ratings_data.append({
                    'id': rating.id,
                    'title': rating.title,
                    'content': rating.content,
                    'rating': rating.rating,
                    'datetime': str(rating.datetime),
                    'author': rating.author
                })
            film_data.append({
                'id': film.id,
                'title': film.title,
                'year': film.year,
                'genre': film.genre,
                'description': film.description,
                'director': film.director,
                'actors': film.actors,
                'ratings': ratings_data,
                'average_rating': film.average_rating
            })

        return func.HttpResponse(json.dumps(film_data), status_code=200)

    elif req.method == "POST":
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse("Invalid JSON", status_code=400)
        
        title = req_body.get('title')
        year = req_body.get('year')
        genre = req_body.get('genre')
        description = req_body.get('description')
        director = req_body.get('director')
        actors = req_body.get('actors')

        if not all([title, year, genre, description, director, actors]):
            return func.HttpResponse("Missing required fields", status_code=400)
        
        new_film = models.Film(title, year, genre, description, director, actors)

        session = Session()
        session.add(new_film)
        session.commit()
        session.close()

        return func.HttpResponse("Film added", status_code=200)

@app.route(route="rating", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def rating(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)
    
    title = req_body.get('title')
    content = req_body.get('content')
    rating = req_body.get('rating')
    datetime = dt.datetime.now()
    author = req_body.get('author')
    film_id = req_body.get('film_id')

    if not all([title, content, rating, author, film_id]):
        return func.HttpResponse("Missing required fields", status_code=400)
    if not isinstance(rating, int):
        return func.HttpResponse("Rating must be an integer", status_code=400)
    if rating < 1 or rating > 10:
        return func.HttpResponse("Rating must be between 1 and 10", status_code=400)
    
    session = Session()
    film = session.query(models.Film).filter(models.Film.id == film_id).first()
    if not film:
        return func.HttpResponse("Film not found", status_code=404)
    
    new_rating = models.Rating(title, content, rating, datetime, author, film)

    session.add(new_rating)
    session.commit()
    session.close()

    return func.HttpResponse("Rating added", status_code=200)

@app.timer_trigger(schedule="0 30 11 * * *", arg_name="timer", run_on_startup=False, use_monitor=False)
def calculate_average_rating(timer: func.TimerRequest) -> None:
    logging.info('Python timer trigger function ran at %s', dt.datetime.now())

    session = Session()
    films = session.query(models.Film).all()
    for film in films:
        ratings = session.query(models.Rating).filter(models.Rating.film_id == film.id).all()
        if ratings:
            average_rating = sum([rating.rating for rating in ratings]) / len(ratings)
            film.average_rating = average_rating
            session.commit()
    session.close()

    return