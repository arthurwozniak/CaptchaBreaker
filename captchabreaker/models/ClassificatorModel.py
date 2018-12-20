from . import db

class ClassificatorModel(db.Model):
    __tablename__ = 'classificators'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    name = db.Column(db.String, nullable=False)
    network = db.Column(db.String)
    task_id = db.Column(db.String, nullable=False)
    is_finished = db.Column(db.Boolean, default=False, nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    def __repr__(self):
        return "<classificator %s>" % self.name