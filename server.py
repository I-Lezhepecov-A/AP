import sqlite3

from flask import Flask, request  # noqa

from common import created, no_content, not_found, ok

app = Flask(__name__)


def get_db_connection():
    if app.config['TESTING']:
        conn = sqlite3.connect('zadacha_test.db')
    else:
        conn = sqlite3.connect('zadacha.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/vaccinations',  methods=["GET"])
def get_vaccinations():
    conn = get_db_connection()
    vaccinations = conn.execute('''SELECT json_group_array(
        json_object(
        'name', name,
        'iso_code', iso_code,
        'population', population,
        'total_vaccinated', total_vaccinated,
        'percentage_vaccinated', percentage_vaccinated
        )
    )
    FROM countries;''').fetchall()
    conn.close()
    result = [i for i in dict([i for i in vaccinations][0])][0]
    return ok(dict(vaccinations[0])[result]), 200


@app.route('/vaccinations/<code>',  methods=["GET"])
def get_vaccination(code):
    conn = get_db_connection()
    vaccinations = conn.execute(f"""SELECT
        json_object(
        'name', name,
        'iso_code', iso_code,
        'population', population,
        'total_vaccinated', total_vaccinated,
        'percentage_vaccinated', percentage_vaccinated
    )
    FROM countries where iso_code = '{code}';""").fetchall()
    conn.close()
    try:
        result = [i for i in dict([i for i in vaccinations][0])][0]
        return ok(dict(vaccinations[0])[result]), 200
    except IndexError:
        return not_found(), 404


@app.route('/vaccinations/<code>',  methods=["DELETE"])
def delete_country(code):
    conn = get_db_connection()
    select = conn.execute(f"""SELECT count(name) FROM countries
                           WHERE iso_code ='{code}' """)
    if dict([i for i in select][0])['count(name)']:
        conn.execute(f"""DELETE
            FROM countries where iso_code = '{code}';""").fetchall()
        conn.commit()
        conn.close()
        return no_content(), 204
    return not_found(), 404


@app.route('/vaccinations',  methods=["POST"])
def create_country():
    data = request.json
    name, iso_code, population, total_vaccinated, percentage_vaccinated = \
        data['name'], data['iso_code'], data['population'],\
        data['total_vaccinated'], data['percentage_vaccinated']
    conn = get_db_connection()
    select = conn.execute(f"""SELECT count(name) FROM countries
                           WHERE iso_code ='{iso_code}' """)
    if dict([i for i in select][0])['count(name)']:
        conn.execute(f"""UPDATE countries SET population='{population}',
                     total_vaccinated='{total_vaccinated}',
                     percentage_vaccinated='{percentage_vaccinated}'
                     WHERE iso_code='{iso_code}'""")
        conn.commit()
        conn.close()
        return no_content(), 204

    conn.execute(f"""INSERT INTO countries
                 (name, iso_code, population, total_vaccinated,
                 percentage_vaccinated) VALUES
                 ('{name}', '{iso_code}', '{population}', '{total_vaccinated}',
                 '{percentage_vaccinated}')""")
    conn.commit()
    conn.close()
    return created(), 201
