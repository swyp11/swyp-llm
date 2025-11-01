# Database repositories
from src.database.repositories.recommendation import recommendation_repo
from src.database.repositories.wedding_dress import wedding_dress_repo
from src.database.repositories.survey import survey_repo

__all__ = [
    "recommendation_repo",
    "wedding_dress_repo",
    "survey_repo"
]
