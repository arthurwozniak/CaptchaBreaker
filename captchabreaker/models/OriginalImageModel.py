from . import db


class OriginalImageModel(db.Model):
    __tablename__ = 'original_images'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    data = db.Column(db.String, nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    characters = db.relationship('CharacterModel', backref='original', lazy=False, cascade='all,delete')

    def __repr__(self):
        return "<OriginalImage %s>" % self.text
