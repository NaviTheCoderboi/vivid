from collections.abc import Callable
import typing as t

__all__: tuple[str, ...] = ("send_response",)

async def send_response(status: int, body: t.Any, headers: list[list[str | bytes]], send: Callable):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': headers
    })
    await send({
        'type': 'http.response.body',
        'body': body.encode('utf-8') if isinstance(body, str) else body
    })