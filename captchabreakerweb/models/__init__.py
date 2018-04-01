from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .CharacterModel import CharacterModel
from .DatasetModel import DatasetModel
from .OriginalImageModel import OriginalImageModel