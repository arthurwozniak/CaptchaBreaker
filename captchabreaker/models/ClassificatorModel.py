from . import db
from celery.result import AsyncResult


class ClassificatorModel(db.Model):
    __tablename__ = 'classificators'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    name = db.Column(db.String, nullable=False)
    task_id = db.Column(db.String)
    is_finished = db.Column(db.Boolean, default=False, nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    config = db.Column(db.JSON, nullable=False, default={})
    queries = db.relationship('QueryModel', backref='classificator', lazy=True, cascade="all, delete")

    def __repr__(self):
        return "<ClassificatorModel %s>" % self.name

    @property
    def task(self):
        from captchabreaker import celery
        if self.task_id is not None:
            return celery.AsyncResult(self.task_id)

    @staticmethod
    def finished():
        return ClassificatorModel.query.filter(ClassificatorModel.is_finished)
