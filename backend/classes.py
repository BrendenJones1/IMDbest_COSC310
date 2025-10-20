from typing import List, Dict, Optional
# constructors for current support classes 
class Movie:
    def __init__(self, title: str, rating: int, year: int, director: str, poster: str):
        self.title = title
        self.rating = rating
        self.year = year
        self.director = director
        self.poster = poster

class Review:
    def __init__(self, review_id: str, rating: int, body: str, author: 'User', movie: Movie):
        self.review_id = review_id
        self.rating = rating
        self.body = body
        self.author = author
        self.movie = movie

class Penalty:
    def __init__(self, penalty_id: str, body: str, penalized: 'User'):
        self.penalty_id = penalty_id
        self.body = body
        self.penalized = penalized

class Flag:
    def __init__(self, flag_id: str, body: str, flagged_user: 'User', review: Review):
        self.flag_id = flag_id
        self.body = body
        self.flagged_user = flagged_user
        self.review = review


#USER CLASS
class User:
    def __init__(self, user_id: str, username: str, password: str):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.reviews: List[Review] = []
        self.watchlist: List[Movie] = []
        self.penalties: List[Penalty] = []

    def create_review(self, review_id: str, rating: int, body: str, movie: Movie) -> Review:
        # only one review per movie per user
        for existing in self.reviews:
            if existing.movie.title == movie.title:
                raise ValueError("User has already reviewed this movie")

        review = Review(review_id, rating, body, self, movie)
        self.reviews.append(review)
        return review

    def update_review(self, review_id: str, params: Dict[str, str]) -> Optional[Review]:
        for review in self.reviews:
            if review.review_id == review_id:
                if "rating" in params:
                    review.rating = params["rating"]
                if "body" in params:
                    review.body = params["body"]
                return review
        return None

    def delete_review(self, review_id: str) -> bool:
        for review in self.reviews:
            if review.review_id == review_id:
                self.reviews.remove(review)
                return True
        return False

    def flag_review(self, review: Review, body: str) -> Flag:
        return Flag(flag_id=f"flag_{review.review_id}", body=body, flagged_user=review.author, review=review)


#ADMIN CLASS
class Admin(User):
    def __init__(self, user_id: str, username: str, password: str):
        super().__init__(user_id, username, password)
        self.pending_flags: List[Flag] = []

    def create_movie(self, params: Dict[str, str]) -> Movie:
        return Movie(
            title=params.get("title", ""),
            rating=params.get("rating", 0),
            year=params.get("year", 0),
            director=params.get("director", ""),
            poster=params.get("poster", "")
        )

    def update_movie(self, movie: Movie, params: Dict[str, str]) -> Movie:
        if "title" in params:
            movie.title = params["title"]
        if "rating" in params:
            movie.rating = params["rating"]
        if "year" in params:
            movie.year = params["year"]
        if "director" in params:
            movie.director = params["director"]
        if "poster" in params:
            movie.poster = params["poster"]
        return movie

    def delete_movie(self, movie: Movie, movie_list: List[Movie]) -> bool:
        if movie in movie_list:
            movie_list.remove(movie)
            return True
        return False
