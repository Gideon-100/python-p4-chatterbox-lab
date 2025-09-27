from datetime import datetime
import pytest

from app import app
from models import db, Message

@pytest.fixture(scope="module")
def setup_db():
    """Set up the database and create tables before tests."""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


class TestMessage:
    """Message model in models.py"""

    def test_has_columns_for_body_username_created_at(self, setup_db):
        with app.app_context():
            
            msg = Message(body="Hello 👋", username="Liza")
            db.session.add(msg)
            db.session.commit()

            m = Message.query.filter(
                Message.body == "Hello 👋",
                Message.username == "Liza"
            ).first()

            assert m.body == "Hello 👋"
            assert m.username == "Liza"
            assert isinstance(m.created_at, datetime)

            db.session.delete(m)
            db.session.commit()
