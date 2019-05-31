from . import db

class DatasetModel(db.Model):
    __tablename__ = 'datasets'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    name = db.Column(db.String)
    config = db.Column(db.JSON, nullable=False, default={})
    original_images = db.relationship('OriginalImageModel', backref='dataset', lazy=True, cascade='all,delete')
    classificators = db.relationship('ClassificatorModel', backref='dataset', lazy=True)
    known_characters = db.Column(db.String)
    characters_per_image = db.Column(db.Integer)

    def __repr__(self):
        return "<DatasetModel %s>" % self.name
