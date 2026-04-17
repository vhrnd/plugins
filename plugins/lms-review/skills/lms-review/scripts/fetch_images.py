#!/usr/bin/env python3

import argparse
import hashlib
import json
import mimetypes
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_MAX_BYTES = 15 * 1024 * 1024
DEFAULT_OUTPUT_DIR = Path(tempfile.gettempdir()) / "lms-review-media"
CHUNK_SIZE = 64 * 1024
CONTENT_TYPE_EXTENSION_MAP = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/bmp": ".bmp",
    "image/x-icon": ".ico",
    "image/tiff": ".tiff",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/ogg": ".ogg",
    "audio/webm": ".webm",
}


@dataclass(slots=True)
class MediaRequest:
    source_url: str
    question_index: int | None = None
    media_role: str | None = None
    source_field: str | None = None
    answer_index: int | None = None

    def context_dict(self) -> dict[str, Any]:
        payload = {
            "question_index": self.question_index,
            "media_role": self.media_role,
            "source_field": self.source_field,
            "answer_index": self.answer_index,
        }
        return {key: value for key, value in payload.items() if value is not None}


@dataclass(slots=True)
class DownloadResult:
    source_url: str
    status: str
    local_path: str | None = None
    metadata_path: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None
    cache_hit: bool = False
    error_code: str | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "source_url": self.source_url,
            "status": self.status,
            "local_path": self.local_path,
            "metadata_path": self.metadata_path,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "cache_hit": self.cache_hit,
            "error_code": self.error_code,
            "message": self.message,
        }
        return {key: value for key, value in payload.items() if value is not None}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and cache LMS review media from public URLs.",
    )
    parser.add_argument(
        "--url",
        dest="urls",
        action="append",
        default=[],
        help="Public media URL. May be passed multiple times.",
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        help=(
            "Path to a JSON array of URLs/items, or an object with a top-level "
            "'urls' or 'items' array."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for cached images. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        help="Optional file path for the JSON manifest. Stdout is always written.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"HTTP timeout in seconds. Default: {DEFAULT_TIMEOUT_SECONDS}",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_MAX_BYTES,
        help=f"Abort files larger than this many bytes. Default: {DEFAULT_MAX_BYTES}",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore cache and re-download every URL.",
    )
    return parser


def _parse_media_request(item: Any) -> MediaRequest:
    if isinstance(item, str):
        normalized = item.strip()
        if not normalized:
            raise ValueError("Media URL entries must not be empty")
        return MediaRequest(source_url=normalized)

    if not isinstance(item, dict):
        raise ValueError("Media entries must be either a URL string or an object")

    raw_url = item.get("url")
    if raw_url is None:
        raise ValueError("Structured media entries must include a 'url' field")

    normalized = str(raw_url).strip()
    if not normalized:
        raise ValueError("Structured media entry 'url' must not be empty")

    question_index = item.get("question_index")
    if question_index is not None:
        question_index = int(question_index)

    answer_index = item.get("answer_index")
    if answer_index is not None:
        answer_index = int(answer_index)

    media_role = item.get("media_role")
    if media_role is not None:
        media_role = str(media_role).strip() or None

    source_field = item.get("source_field")
    if source_field is not None:
        source_field = str(source_field).strip() or None

    return MediaRequest(
        source_url=normalized,
        question_index=question_index,
        media_role=media_role,
        source_field=source_field,
        answer_index=answer_index,
    )


def _load_requests(args: argparse.Namespace) -> list[MediaRequest]:
    requests = [_parse_media_request(url) for url in args.urls]
    if args.input_json is not None:
        raw = json.loads(args.input_json.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict) and isinstance(raw.get("urls"), list):
            items = raw["urls"]
        elif isinstance(raw, dict) and isinstance(raw.get("items"), list):
            items = raw["items"]
        else:
            raise ValueError(
                "--input-json must contain a JSON array or an object with a 'urls' or "
                "'items' array"
            )
        requests.extend(_parse_media_request(item) for item in items)

    return _dedupe_requests(requests)


def _dedupe_requests(requests: list[MediaRequest]) -> list[MediaRequest]:
    seen_simple_urls: set[str] = set()
    ordered: list[MediaRequest] = []
    for request in requests:
        context = request.context_dict()
        if context:
            ordered.append(request)
            continue
        if request.source_url in seen_simple_urls:
            continue
        seen_simple_urls.add(request.source_url)
        ordered.append(request)
    return ordered


def _url_cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _guess_extension(url: str, mime_type: str | None) -> str:
    if mime_type:
        normalized = mime_type.split(";", 1)[0].strip().lower()
        if normalized in CONTENT_TYPE_EXTENSION_MAP:
            return CONTENT_TYPE_EXTENSION_MAP[normalized]
        guessed = mimetypes.guess_extension(normalized, strict=False)
        if guessed:
            return guessed

    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix:
        return suffix
    return ".img"


def _cached_result(url: str, output_dir: Path) -> DownloadResult | None:
    cache_key = _url_cache_key(url)
    for metadata_path in output_dir.glob(f"{cache_key}.*.json"):
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        local_path = Path(payload["local_path"])
        if local_path.exists():
            return DownloadResult(
                source_url=url,
                status="ok",
                local_path=str(local_path),
                metadata_path=str(metadata_path),
                mime_type=payload.get("mime_type"),
                size_bytes=payload.get("size_bytes"),
                sha256=payload.get("sha256"),
                cache_hit=True,
            )
    return None


def _result_for_request(request: MediaRequest, download_result: DownloadResult) -> dict[str, Any]:
    payload = download_result.to_dict()
    payload.update(request.context_dict())
    return payload


def _download_media(url: str, output_dir: Path, timeout: float, max_bytes: int) -> DownloadResult:
    request = Request(url, headers={"User-Agent": "lms-review-fetch-images/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            content_type = response.headers.get_content_type().lower()
            if not content_type.startswith(("image/", "audio/")):
                return DownloadResult(
                    source_url=url,
                    status="error",
                    error_code="unsupported_media_type",
                    message=f"Expected image/audio content, got {content_type}",
                )

            buffer = bytearray()
            content_hash = hashlib.sha256()
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                buffer.extend(chunk)
                content_hash.update(chunk)
                if len(buffer) > max_bytes:
                    return DownloadResult(
                        source_url=url,
                        status="error",
                        error_code="file_too_large",
                        message=f"File exceeded max_bytes={max_bytes}",
                    )

    except HTTPError as exc:
        return DownloadResult(
            source_url=url,
            status="error",
            error_code=f"http_{exc.code}",
            message=str(exc),
        )
    except URLError as exc:
        return DownloadResult(
            source_url=url,
            status="error",
            error_code="network_error",
            message=str(exc.reason),
        )

    cache_key = _url_cache_key(url)
    extension = _guess_extension(url, content_type)
    local_path = output_dir / f"{cache_key}{extension}"
    metadata_path = output_dir / f"{cache_key}{extension}.json"
    local_path.write_bytes(buffer)

    metadata = {
        "source_url": url,
        "local_path": str(local_path),
        "mime_type": content_type,
        "size_bytes": len(buffer),
        "sha256": content_hash.hexdigest(),
        "downloaded_at": datetime.now(UTC).isoformat(),
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=True, indent=2), encoding="utf-8")
    return DownloadResult(
        source_url=url,
        status="ok",
        local_path=str(local_path),
        metadata_path=str(metadata_path),
        mime_type=content_type,
        size_bytes=len(buffer),
        sha256=content_hash.hexdigest(),
        cache_hit=False,
    )


def fetch_images(
    items: list[str | dict[str, Any]],
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = DEFAULT_MAX_BYTES,
    force: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    requests = _dedupe_requests([_parse_media_request(item) for item in items])
    results: list[dict[str, Any]] = []
    resolved_by_url: dict[str, DownloadResult] = {}
    for request in requests:
        cached_or_downloaded = resolved_by_url.get(request.source_url)
        if cached_or_downloaded is None:
            if not force:
                cached_or_downloaded = _cached_result(request.source_url, output_dir)
            if cached_or_downloaded is None:
                cached_or_downloaded = _download_media(
                    request.source_url,
                    output_dir=output_dir,
                    timeout=timeout,
                    max_bytes=max_bytes,
                )
            resolved_by_url[request.source_url] = cached_or_downloaded

        results.append(_result_for_request(request, cached_or_downloaded))

    return {
        "output_dir": str(output_dir),
        "item_count": len(results),
        "items": results,
    }


def _requests_to_cli_items(requests: list[MediaRequest]) -> list[str | dict[str, Any]]:
    items: list[str | dict[str, Any]] = []
    for request in requests:
        context = request.context_dict()
        if not context:
            items.append(request.source_url)
            continue
        payload = {"url": request.source_url, **context}
        items.append(payload)
    return items


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        requests = _load_requests(args)
    except ValueError as exc:
        parser.error(str(exc))

    if not requests:
        parser.error("At least one --url or --input-json entry is required")

    manifest = fetch_images(
        _requests_to_cli_items(requests),
        output_dir=args.output_dir,
        timeout=args.timeout,
        max_bytes=args.max_bytes,
        force=args.force,
    )
    payload = json.dumps(manifest, ensure_ascii=True, indent=2)
    if args.manifest_out is not None:
        args.manifest_out.write_text(payload + "\n", encoding="utf-8")
    sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
