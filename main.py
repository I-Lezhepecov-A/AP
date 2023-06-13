import csv
import sqlite3


def perform_insert(db_name):
    COMMON_DATA = {}
    PREPARED_VALUES = []
    with open("./data/country_populations.csv", 'r') as file:
        csvreader = list(csv.reader(file))
        header = [i for i in csvreader][0]
        index_header_2020 = [i for i, v in enumerate(header) if v == '2020'][0]
        for row in csvreader[1:]:
            if 'OWID_' in row[1]:
                continue
            name, iso_code, population = row[0], row[1], row[index_header_2020]
            country_template = {
                'name': name.replace("'", "`"),
                'iso_code': iso_code,
                'population': population,
                'total_vaccinated': 0,
                'percentage_vaccinated': 0
            }

            row[1], row[index_header_2020]
            COMMON_DATA[row[1]] = country_template

    with open("./data/vaccinations.csv", 'r') as file:
        csvreader = list(csv.reader(file))
        for row in csvreader[1:]:
            if 'OWID_' in row[1]:
                continue
            try:
                country_in_common = COMMON_DATA[row[1]]
                country_in_common['total_vaccinated'] = int(row[5] or 0) 
                country_in_common['percentage_vaccinated'] = \
                    country_in_common['total_vaccinated'] \
                    / int(country_in_common['population'])
            except KeyError:
                continue
    for data in COMMON_DATA:
        params = COMMON_DATA[data]
        PREPARED_VALUES.append(
            "('{}', '{}', '{}', '{}', '{}')".format(
                params['name'],
                params['iso_code'],
                params['population'],
                params['total_vaccinated'],
                params['percentage_vaccinated']
                ))

    insert_template = f'''INSERT INTO countries
                (name, iso_code, population, total_vaccinated,
                percentage_vaccinated) VALUES
                {", ".join(PREPARED_VALUES)}
                '''
    con = sqlite3.connect(db_name)

    cur = con.cursor()
    cur.execute(insert_template)
    con.commit()
    con.close()


if __name__ == '__main__':
    import sys
    db_name = sys.argv[1]
    perform_insert(db_name)
