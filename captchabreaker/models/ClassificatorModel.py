from . import db
from celery.result import AsyncResult

class ClassificatorModel(db.Model):
    __tablename__ = 'classificators'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    name = db.Column(db.String, nullable=False)
    network = db.Column(db.String)
    task_id = db.Column(db.String)
    is_finished = db.Column(db.Boolean, default=False, nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    config = db.Column(db.JSON, nullable=False, default={})

    def __repr__(self):
        return "<classificator %s>" % self.name

    @property
    def task(self):
        return AsyncResult(self.task_id, backend=AsyncResult(self.task_id).backend)

    @staticmethod
    def finished():
        return ClassificatorModel.query.filter(ClassificatorModel.is_finished == True)