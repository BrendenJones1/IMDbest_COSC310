import pytest

from backend.repositories import movie_repo as movie_repo_module
from backend.repositories.movie_repo import MovieRepository


def test_search_movies_raises_on_repository_error(monkeypatch):
    """
    Fault injection / mocking test for the movie repository search path.

    We simulate a low-level repository failure by forcing
    MovieRepository.list_movies to raise OSError when search_movies
    calls it. The goal is to show that tests cover error paths and
    not only the happy path.
    """

    def fake_list_movies(include_metadata: bool = False):
        raise OSError("simulated repository error")

    # Patch the MovieRepository.list_movies method so that any call
    # from search_movies will hit our injected error.
    monkeypatch.setattr(
        movie_repo_module.MovieRepository,
        "list_movies",
        fake_list_movies,
        raising=True,
    )

    # Verify that the error is propagated and that the injected message appears.
    with pytest.raises(OSError) as excinfo:
        MovieRepository.search_movies(q="a", include_metadata=False)

    assert "simulated repository error" in str(excinfo.value)
