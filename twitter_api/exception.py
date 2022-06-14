import json.decoder


class HTTPException(Exception):
    """ HTTPException """

    def __init__(self, response):
        self.response = response

        self.api_errors = []
        self.api_codes = []
        self.api_messages = []

        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError:
            super().__init__(f"{response.status_code} {response.reason}")
        else:
            errors = response_json.get("errors", [])
            # Use := when support for Python 3.7 is dropped
            if "error" in response_json:
                errors.append(response_json["error"])
            error_text = ""
            for error in errors:
                self.api_errors.append(error)
                if "code" in error:
                    self.api_codes.append(error["code"])
                if "message" in error:
                    self.api_messages.append(error["message"])
                if "code" in error and "message" in error:
                    error_text += f"\n{error['code']} - {error['message']}"
                elif "message" in error:
                    error_text += '\n' + error["message"]
            super().__init__(
                f"{response.status_code} {response.reason}{error_text}"
            )


class TooManyRequests(HTTPException):
    """Too many requests"""
    pass


class TwitterServerError(HTTPException):
    """Too many requests"""
    pass
