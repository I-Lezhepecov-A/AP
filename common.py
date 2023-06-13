import json


def ok(data):
    return {'status_code': 200,
            'data': json.loads(data)}


def created():
    return {'status_code': 201,
            'data': 'Created'}


def no_content():
    return {'status_code': 204}


def not_found():
    return {'status_code': 404,
            'data': 'Not Found'}
