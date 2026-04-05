from libs.config import Config


def generate_error_response(msg=None, data=None):
    if msg:
        response = {"status": msg[0], "message": msg[1], "data": data}
    else:
        msg = Config.Generic.BAD_REQUEST
        response = {"status": msg[0], "message": msg[1], "data": data}

    return response


def generate_success_response(data=None, msg=Config.Generic.SUCCESS):
    response = {"status": msg[0], "message": msg[1], "data": data}
    return response


def generate_error_response_with_subtitle(msg=None, data=None):
    if msg:
        response = {
            "status": msg[0],
            "error_title": msg[1],
            "error_sub_title": msg[2],
            "data": {"error_title": msg[1], "error_sub_title": msg[2]},
        }
    else:
        msg = Config.Generic.BAD_REQUEST
        response = {
            "status": msg[0],
            "error_title": msg[1],
            "error_sub_title": None,
            "data": {"error_title": msg[1], "error_sub_title": msg[2]},
        }

    return response
