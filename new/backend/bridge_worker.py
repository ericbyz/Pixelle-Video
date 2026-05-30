import base64
import json
import sys
import traceback

from fastapi.testclient import TestClient

from main import app


HOP_BY_HOP_HEADERS = {
    "connection",
    "content-encoding",
    "content-length",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def _filtered_headers(headers: dict) -> dict:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }


def handle_request(client: TestClient, request: dict) -> dict:
    body = base64.b64decode(request.get("body", ""))
    response = client.request(
        request["method"],
        request["url"],
        headers=_filtered_headers(request.get("headers", {})),
        content=body,
    )

    return {
        "id": request["id"],
        "status": response.status_code,
        "headers": _filtered_headers(dict(response.headers)),
        "body": base64.b64encode(response.content).decode("ascii"),
    }


def main() -> int:
    with TestClient(app) as client:
        for line in sys.stdin:
            if not line.strip():
                continue

            try:
                request = json.loads(line)
                result = handle_request(client, request)
            except Exception as exc:
                result = {
                    "id": request.get("id") if "request" in locals() else None,
                    "status": 500,
                    "headers": {"content-type": "application/json"},
                    "body": base64.b64encode(json.dumps({
                        "detail": str(exc),
                        "traceback": traceback.format_exc(),
                    }).encode("utf-8")).decode("ascii"),
                }

            sys.stdout.write(json.dumps(result, separators=(",", ":")) + "\n")
            sys.stdout.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
