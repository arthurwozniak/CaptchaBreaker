from . import db

class QueryModel(db.Model):
    __tablename__ = 'queries'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    classificator_id = db.Column(db.Integer, db.ForeignKey('classificators.id'), nullable=True)

    def __repr__(self):
        return "<QueryModel %s>" % self.id
