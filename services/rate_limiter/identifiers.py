# we had IP as identifier but it would create broblem if some people were using same WIFI
# therefore we will use different types of identifiers as per need

# basically this will tell who is making the request

from fastapi import Request


def client_ip(request: Request) -> str:
    """
    Returns the client's IP address.
    """

    return request.client.host