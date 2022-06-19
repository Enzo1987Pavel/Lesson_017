from flask import Flask, request
from flask_restx import Api, Resource

from Schemas import movie_schema, movies_schema
from Models import Movie, Director, Genre
from setup_db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JSON_AS_ASCII"] = False

app.app_context().push()  # Связываем контекст приложения с текущим содержимым

db.init_app(app)  # Связывание БД с приложением из файла 'setup_db'

api = Api(app)
movie_ns = api.namespace("movies")


@movie_ns.route("/")  # Показ всех фильмов
class MovieView(Resource):
    def get(self):  # Вывод всех фильмов
        all_movie_filter = db.session.query(Movie.id, Movie.title, Movie.description, Movie.trailer, Movie.year, Movie.rating,
                                            Genre.name.label("genre"),
                                            Director.name.label("director")).join(Genre).join(Director)

        dir_id = request.args.get("director_id")
        gen_id = request.args.get("genre_id")

        if "director_id" in request.args:  # Ищем фильм с определенным режиссером
            all_movie_filter = all_movie_filter.filter(Movie.director_id == dir_id)

        if "genre_id" in request.args:  # Ищем фильм с определенным жанром
            all_movie_filter = all_movie_filter.filter(Movie.genre_id == gen_id)

        all_movies = all_movie_filter.all()

        return movies_schema.dump(all_movies), 200

    def post(self):  # Добавление одного фильма
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)

        return f"Фильм с id = {new_movie.id} успешно создан!", 201


@movie_ns.route("/<int:movie_id>")  # Отображение выбранного фильма по его 'id'
class MovieView(Resource):
    def get(self, movie_id: int):
        one_movie = db.session.query(Movie.id, Movie.title, Movie.description, Movie.trailer, Movie.year, Movie.rating,
                                     Genre.name.label("genre"),
                                     Director.name.label("director")).join(Genre).join(Director).\
                                     filter(Movie.id == movie_id).first()

        if one_movie:  # Если найден фильм в списке - то выводим его данные
            return movie_schema.dump(one_movie), 200
        return f"Выбранного фильма с id = {movie_id} не найдено!", 404

    def patch(self, movie_id: int):  # Выводим частичные изменения в данных фильма
        edit_part_of_movie = db.session.query(Movie).get(movie_id)

        if not edit_part_of_movie:  # Если не найден фильм в списке - то выводим сообщение
            return f"Выбранного фильма с id = {movie_id} не найдено!", 404

        req_json = request.json
        if "title" in req_json:
            edit_part_of_movie.title = req_json["title"]
        elif "description" in req_json:
            edit_part_of_movie.description = req_json["description"]
        elif "trailer" in req_json:
            edit_part_of_movie.trailer = req_json["trailer"]
        elif "year" in req_json:
            edit_part_of_movie.year = req_json["year"]
        elif "rating" in req_json:
            edit_part_of_movie.rating = req_json["rating"]
        elif "genre_id" in req_json:
            edit_part_of_movie.genre_id = req_json["genre_id"]
        elif "director_id" in req_json:
            edit_part_of_movie.director_id = req_json["director_id"]

        db.session.add(edit_part_of_movie)
        db.session.commit()

        return f"Фильм с id = {edit_part_of_movie.id} успешно обновлен!", 204

    def put(self, movie_id: int):  # Выводим полные изменения в данных фильма
        edit_all_movie = db.session.query(Movie).get(movie_id)

        if not edit_all_movie:  # Если не найден фильм в списке - то выводим сообщение об ошибке
            return f"Выбранного фильма с id = {movie_id} не найдено!", 404

        req_json = request.json

        edit_all_movie.title = req_json["title"]
        edit_all_movie.description = req_json["description"]
        edit_all_movie.trailer = req_json["trailer"]
        edit_all_movie.year = req_json["year"]
        edit_all_movie.rating = req_json["rating"]
        edit_all_movie.genre_id = req_json["genre_id"]
        edit_all_movie.director_id = req_json["director_id"]

        db.session.add(edit_all_movie)
        db.session.commit()

        return f"Фильм с id = {edit_all_movie.id} успешно обновлен!", 204

    def delete(self, movie_id: int):
        del_movie = db.session.query(Movie).get(movie_id)

        if not del_movie:  # Если не найден фильм в списке - то выводим сообщение
            return f"Выбранного фильма с id = {movie_id} не найдено!", 404

        db.session.delete(del_movie)
        db.session.commit()

        return f"Фильм с id = {del_movie.id} успешно удален!", 204


if __name__ == '__main__':
    app.run(debug=True)
