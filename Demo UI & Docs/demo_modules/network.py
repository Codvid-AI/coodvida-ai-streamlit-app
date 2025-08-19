import requests
import json
import typing

server_url: str | None = None
schema_version: str | None = "4.0"


def init(url):
    global server_url
    server_url = url


def send(
    route: str,
    content: dict | None = None,
    session_token: str = None,
    method: str = "POST",
    stream=False,
    verify_ssl=True,
):
    """
    Sends an HTTP request to the backend server.

    Args:
        route (str): The API route.
        content (dict, optional): JSON data for the request body. Defaults to None.
        session_token (str, optional): JWT token for authentication. Defaults to None.
        method (str, optional): HTTP method (GET, POST, PUT, DELETE). Defaults to "POST".
        stream (bool): If True, streams the response. Defaults to False.
        verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to True.

    Yields:
        dict: Chunks of JSON response if `stream` is True.

    Returns:
        RequestResult: Object with response text, status code, and exception if `stream` is False.
    """

    if server_url.endswith("/") and route.startswith("/"):
        route = route[1:]
    elif not server_url.endswith("/") and not route.startswith("/"):
        route = "/" + route

    url = server_url + route
    headers = {}
    data = None

    if session_token:
        headers["Authorization"] = f"Bearer {session_token}"

    if content:
        # For POST/PUT requests, send JSON body
        headers["Content-Type"] = "application/json"
        data = {
            "schema_version": schema_version,
            "data": content if content is not None else {},
        }
        json_str = json.dumps(data, ensure_ascii=False)
        print(f"Sending {method} JSON: {json_str}")

    # ----- stream -----
    if stream:
        try:
            response = requests.request(
                method=method,
                url=url,
                data=json_str if data else None,
                headers=headers,
                verify=verify_ssl,
                stream=True,
            )
            def iter_json():
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        try:
                            yield json.loads(chunk)
                        except Exception as e:
                            print(f"Error parsing streamed chunk: {e}\nRaw: {chunk}")
                response.close()
            return iter_json()
        except Exception as e:
            print(f"Streaming request failed: {e}")
            
    # ----- normal send -----
    else:
        try:
            response = requests.request(
                method, url, headers=headers, data=json_str if data else None, verify=verify_ssl
            )

            status_code = response.status_code
            result = RequestResult(response.text, status_code, exception=None)
        except Exception as e:
            result = RequestResult(None, None, exception=e)
        return result


class RequestResult:
    def __init__(self, text: str | None, status_code: int, exception: Exception):
        self.text = text
        self.status_code = status_code
        self.exception = exception

    def get_dict(self) -> dict | typing.Any | None:
        try:
            return json.loads(self.text)
        except:
            return None

    def __str__(self):
        txt = ""
        txt += f"- Status Code: {self.status_code}\n"
        if self.text:
            dic = self.get_dict()
            if dic:
                txt += "- Response (json):\n"
                txt += json.dumps(dic, indent=4, ensure_ascii=False) + "\n"
            else:
                txt += "- Response (text):\n"
                txt += self.text + "\n"
        else:
            txt += "- No response body.\n"
        if self.exception:
            txt += "- Error:\n" + str(self.exception)
        return txt

    def print(self):
        print(self)
