from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Film(Base):
    __tablename__ = 'films'

    id = Column(Integer, primary_key=True)
    title = Column(String(length=255))
    year = Column(Integer)
    genre = Column(String(length=255))
    description = Column(Text)
    director = Column(String(length=255))
    actors = Column(String(length=255))
    average_rating = Column(Float)

    def __init__(self, title, year, genre, description, director, actors):
        self.title = title
        self.year = year
        self.genre = genre
        self.description = description
        self.director = director
        self.actors = actors

class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    title = Column(String(length=255))
    content = Column(Text)
    rating = Column(Integer)
    datetime = Column(DateTime)
    author = Column(String(length=255))
    film_id = Column(Integer, ForeignKey('films.id'))
    film = relationship('Film', backref='ratings')

    def __init__(self, title, content, rating, datetime, author, film):
        self.title = title
        self.content = content
        self.rating = rating
        self.datetime = datetime
        self.author = author
        self.film = film