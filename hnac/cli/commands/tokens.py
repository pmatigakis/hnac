from flask_script import Command, Option
from sqlalchemy.exc import SQLAlchemyError

from hnac.models import Token
from hnac.web.database import db


class CreateToken(Command):
    option_list = (
        Option("token_name"),
    )

    def run(self, token_name):
        token = Token.create(db.session, token_name)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            print("failed to create token")
            return

        print(token.value)


class ListTRokens(Command):
    def run(self):
        for token in Token.all(db.session):
            print("{} - {}".format(token.id, token.name))


class GetToken(Command):
    option_list = (
        Option("token_name"),
    )

    def run(self, token_name):
        token = Token.get_by_name(db.session, token_name)

        if token is None:
            print("Unknown token")
            return

        print(token.value)


class DeleteToken(Command):
    option_list = (
        Option("token_name"),
    )

    def run(self, token_name):
        token = Token.get_by_name(db.session, token_name)

        if token is None:
            print("Unknown token")
            return

        token.delete(db.session)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            print("failed to delete token")
            return
