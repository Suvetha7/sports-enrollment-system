from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.db import DB_PATH, database_has_seed_data, init_database
from src.seed_data import seed_demo_data
from src.services import (
    ValidationError,
    analytics_overview,
    authenticate_user,
    dashboard_payload,
    enroll_user_in_program,
    list_programs,
    register_user,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "static"


def bootstrap_database() -> None:
    init_database(DB_PATH)
    if not database_has_seed_data(DB_PATH):
        seed_demo_data(DB_PATH)


class SportsPortalHandler(BaseHTTPRequestHandler):
    server_version = "SportsPortal/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route in ("/", "/index.html"):
            self._serve_static("index.html")
            return
        if route.startswith("/static/"):
            self._serve_static(route.removeprefix("/static/"))
            return
        if route == "/api/health":
            self._send_json({"status": "ok"})
            return
        if route == "/api/programs":
            self._send_json({"programs": list_programs(DB_PATH)})
            return
        if route == "/api/analytics":
            self._send_json(analytics_overview(DB_PATH))
            return
        if route == "/api/dashboard":
            self._send_json(dashboard_payload(DB_PATH))
            return

        self._send_json({"error": "Route not found."}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path
        payload = self._read_json_body()
        if payload is None:
            return

        try:
            if route == "/api/register":
                created = register_user(payload, DB_PATH)
                self._send_json(
                    {"message": "Registration completed successfully.", "user": created},
                    status=HTTPStatus.CREATED,
                )
                return
            if route == "/api/login":
                user = authenticate_user(payload.get("email", ""), payload.get("password", ""), DB_PATH)
                self._send_json({"message": "Login successful.", "user": user})
                return
            if route == "/api/enroll":
                result = enroll_user_in_program(
                    payload.get("email", ""),
                    int(payload.get("program_id", 0)),
                    payload.get("notes", ""),
                    DB_PATH,
                )
                self._send_json({"message": "Enrollment confirmed.", "result": result})
                return
        except ValidationError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        except ValueError:
            self._send_json({"error": "Program ID must be a valid number."}, status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:  # pragma: no cover - safety net for manual demo
            self._send_json({"error": f"Server error: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_json({"error": "Route not found."}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _read_json_body(self) -> dict | None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"error": "Request body must be valid JSON."}, status=HTTPStatus.BAD_REQUEST)
            return None

    def _serve_static(self, relative_path: str) -> None:
        target = (STATIC_DIR / relative_path).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        mime_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        content = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    bootstrap_database()
    server = ThreadingHTTPServer((host, port), SportsPortalHandler)
    print(f"Sports portal running on http://{host}:{port}")
    server.serve_forever()

