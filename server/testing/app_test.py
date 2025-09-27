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


@pytest.fixture
def client():
    """Flask test client."""
    with app.test_client() as client:
        yield client


class TestApp:
    """Flask application in app.py"""

    def test_has_correct_columns(self, setup_db):
        with app.app_context():
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza"
            )
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

            db.session.delete(hello_from_liza)
            db.session.commit()

    def test_returns_list_of_json_objects_for_all_messages_in_database(self, setup_db, client):
        with app.app_context():
            msg = Message(body="Hello 👋", username="Liza")
            db.session.add(msg)
            db.session.commit()

            response = client.get('/messages')
            records = Message.query.all()

            for message in response.json:
                assert message['id'] in [record.id for record in records]
                assert message['body'] in [record.body for record in records]

            db.session.delete(msg)
            db.session.commit()

    def test_creates_new_message_in_the_database(self, setup_db, client):
        with app.app_context():
            client.post('/messages', json={
                "body": "Hello 👋",
                "username": "Liza",
            })

            h = Message.query.filter_by(body="Hello 👋").first()
            assert h

            db.session.delete(h)
            db.session.commit()

    def test_returns_data_for_newly_created_message_as_json(self, setup_db, client):
        with app.app_context():
            response = client.post('/messages', json={
                "body": "Hello 👋",
                "username": "Liza",
            })

            assert response.content_type == 'application/json'
            assert response.json["body"] == "Hello 👋"
            assert response.json["username"] == "Liza"

            h = Message.query.filter_by(body="Hello 👋").first()
            db.session.delete(h)
            db.session.commit()

    def test_updates_body_of_message_in_database(self, setup_db, client):
        with app.app_context():
            msg = Message(body="Hello 👋", username="Liza")
            db.session.add(msg)
            db.session.commit()

            client.patch(f'/messages/{msg.id}', json={"body": "Goodbye 👋"})

            updated = Message.query.filter_by(body="Goodbye 👋").first()
            assert updated

            db.session.delete(updated)
            db.session.commit()

    def test_returns_data_for_updated_message_as_json(self, setup_db, client):
        with app.app_context():
            msg = Message(body="Hello 👋", username="Liza")
            db.session.add(msg)
            db.session.commit()

            response = client.patch(f'/messages/{msg.id}', json={"body": "Goodbye 👋"})
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Goodbye 👋"

            updated = Message.query.filter_by(body="Goodbye 👋").first()
            db.session.delete(updated)
            db.session.commit()

    def test_deletes_message_from_database(self, setup_db, client):
        with app.app_context():
            msg = Message(body="Hello 👋", username="Liza")
            db.session.add(msg)
            db.session.commit()

            client.delete(f'/messages/{msg.id}')

            deleted = Message.query.filter_by(body="Hello 👋").first()
            assert deleted is None
