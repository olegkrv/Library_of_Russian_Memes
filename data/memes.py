import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

from .users import User


class Memes(SqlAlchemyBase):
    __tablename__ = 'memes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    typpe = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    meme_class = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User', backref='memes')
