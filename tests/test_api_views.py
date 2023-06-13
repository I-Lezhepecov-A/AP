import sqlite3
import subprocess

from server import app

app.config.update({
        "TESTING": True,
    })


def get_db_connection():
    conn = sqlite3.connect('zadacha_test.db')
    conn.row_factory = sqlite3.Row
    return conn


def test_prepare_test_db():
    conn = get_db_connection()
    conn.execute('DROP TABLE IF EXISTS countries;')
    conn.execute('''CREATE TABLE countries
                 (name text, iso_code text, population int,
                 total_vaccinated int, percentage_vaccinated real)''')
    conn.commit()
    subprocess.run(["python", 'main.py', 'zadacha_test.db'])


def test_get_countries():
    flask_app = app
    with flask_app.test_client() as test_client:
        response = test_client.get('/vaccinations')
        assert response.status_code == 200
        conn = get_db_connection()
        count = conn.execute('select count(iso_code) from countries;')
        count_from_db = dict([i for i in count][0])['count(iso_code)']
        assert count_from_db == len(response.json['data'])


def test_get_country():
    flask_app = app
    with flask_app.test_client() as test_client:
        response = test_client.get('/vaccinations/USA')
        assert response.status_code == 200


def test_delete_country():
    flask_app = app
    with flask_app.test_client() as test_client:
        response = test_client.get('/vaccinations/USA')
        assert response.status_code == 200
        response = test_client.delete('/vaccinations/USA')
        assert response.status_code == 204
        response = test_client.get('/vaccinations/USA')
        assert response.status_code == 404


def test_create_country():
    flask_app = app
    with flask_app.test_client() as test_client:
        response = test_client.get('/vaccinations/TEST')
        assert response.status_code == 404
        response = test_client.post('/vaccinations', json={
                                    "name": "Test Country",
                                    "iso_code": "TEST",
                                    "population": 456,
                                    "total_vaccinated": 123,
                                    "percentage_vaccinated": 123/456
                                    })
        assert response.status_code == 201
        response = test_client.get('/vaccinations/TEST')
        assert response.status_code == 200
