from . import db

class CharacterModel(db.Model):

    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    character = db.Column(db.String(1))
    data = db.Column(db.LargeBinary, nullable=True)
    image = db.Column(db.String, nullable=True)
    original_id = db.Column(db.Integer, db.ForeignKey('original_images.id'),
                          nullable=False)

    def __repr__(self):
        return "<CharacterModel %s>" % self.character