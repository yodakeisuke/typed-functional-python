type StatusCode = int

def store_check_api(
      url: str
    ) -> StatusCode:

    if url == "":
        return 404
    return 200
