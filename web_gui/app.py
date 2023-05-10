import fastapi
import uvicorn
from . import widgets
import json
import logging
from datetime import timedelta
from . import common
import timer_dict
import secrets


class App:
    def __init__(
        self,
        app_name: str,
        root_widget: widgets.Widget,
        *,
        domain: str = "localhost",
        port: int = 8000,
    ):
        self.app_name = app_name
        self.root_widget = root_widget
        self.domain = domain
        self.port = port

        # Secrets to authenticate clients over the websocket
        self.session_secrets: timer_dict.TimerDict[str, None] = timer_dict.TimerDict(
            default_duration=timedelta(minutes=5)
        )

        # Fastapi
        self.api = fastapi.FastAPI()
        self.api.add_api_route("/", self._serve_index, methods=["GET"])
        self.api.add_websocket_route("/ws", self._serve_websocket)

    def run(self, *, quiet: bool = True) -> None:
        # Supress stdout messages
        kwargs = {}

        if quiet:
            kwargs["log_config"] = {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": {},
                "handlers": {},
                "loggers": {},
            }

        uvicorn.run(
            self.api,
            host=self.domain,
            port=self.port,
            **kwargs,
        )

    async def _serve_index(self) -> fastapi.responses.HTMLResponse:
        # Dump the widgets
        widgets_json = widgets._serialize(self.root_widget, type(self.root_widget))

        # Come up with a secret to authenticate the websocket
        secret = secrets.token_urlsafe(32)
        self.session_secrets[secret] = None

        # Load the templates
        html = (common.FRONTEND_DIR / "index.html").read_text()
        js = (common.BUILD_DIR / "app.js").read_text()
        css = (common.FRONTEND_DIR / "style.css").read_text()

        # Fill in all placeholders
        js = js.replace(
            "'{root_widget}'",
            json.dumps(widgets_json, indent=4),
        )
        js = js.replace("{session_secret}", secret)

        html = html.replace("{title}", self.app_name)
        html = html.replace("/*{style}*/", css)
        html = html.replace("/*{script}*/", js)

        return fastapi.responses.HTMLResponse(html)

    async def _serve_websocket(
        self,
        session_secret: str,
        websocket: fastapi.WebSocket,
    ):
        # Authenticate the websocket, making sure to remove the secret from the
        # timer dict so it can't be used again
        try:
            self.session_secrets.pop(session_secret)
        except KeyError:
            await websocket.close(code=1008)
            return

        # Accept the websocket
        await websocket.accept()

        while True:
            data = await websocket.receive_json()
            print(data)
