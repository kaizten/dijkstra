#!/usr/bin/env python3
"""Run Dijkstra's algorithm on a JSON adjacency graph loaded from a URI."""

from __future__ import annotations

import argparse
import heapq
import json
import math
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse
from urllib.request import urlopen


Graph = dict[str, dict[str, float]]


class DijkstraError(ValueError):
    """Raised for user-facing input and validation errors."""


def load_uri(uri: str) -> str:
    """Load text from a URI, preferring fsspec when available."""
    try:
        import fsspec  # type: ignore[import-not-found]
    except ImportError:
        fsspec = None

    if fsspec is not None:
        try:
            with fsspec.open(uri, mode="rt", encoding="utf-8") as graph_file:
                return graph_file.read()
        except Exception as exc:
            raise DijkstraError(f"failed to read graph URI with fsspec: {exc}") from exc

    parsed = urlparse(uri)
    if parsed.scheme in ("", "file"):
        path = Path(unquote(parsed.path if parsed.scheme == "file" else uri))
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise DijkstraError(f"failed to read graph file: {exc}") from exc

    if parsed.scheme in ("http", "https"):
        try:
            with urlopen(uri) as response:  # noqa: S310 - User explicitly supplies the URI.
                return response.read().decode("utf-8")
        except OSError as exc:
            raise DijkstraError(f"failed to read graph URL: {exc}") from exc

    raise DijkstraError(
        f"unsupported URI scheme '{parsed.scheme}'. Install fsspec to support more schemes."
    )


def parse_graph(raw_graph: str) -> Graph:
    """Parse and validate a JSON adjacency graph."""
    try:
        payload = json.loads(raw_graph)
    except json.JSONDecodeError as exc:
        raise DijkstraError(f"invalid JSON graph: {exc}") from exc

    if not isinstance(payload, dict):
        raise DijkstraError("graph must be a JSON object mapping nodes to adjacency objects")

    graph: Graph = {}
    for node, edges in payload.items():
        if not isinstance(node, str):
            raise DijkstraError("all node identifiers must be strings")
        if not isinstance(edges, dict):
            raise DijkstraError(f"node '{node}' must map to an adjacency object")

        graph[node] = {}
        for neighbor, weight in edges.items():
            if not isinstance(neighbor, str):
                raise DijkstraError(f"neighbors for node '{node}' must be strings")
            if not isinstance(weight, (int, float)) or isinstance(weight, bool):
                raise DijkstraError(
                    f"edge '{node}' -> '{neighbor}' must have a numeric weight"
                )
            if not math.isfinite(weight):
                raise DijkstraError(
                    f"edge '{node}' -> '{neighbor}' must have a finite weight"
                )
            if weight < 0:
                raise DijkstraError(
                    f"edge '{node}' -> '{neighbor}' must not have a negative weight"
                )
            graph[node][neighbor] = float(weight)

    for edges in graph.values():
        for neighbor in edges:
            graph.setdefault(neighbor, {})

    return graph


def shortest_paths(graph: Graph, source: str) -> tuple[dict[str, float], dict[str, str | None]]:
    """Return shortest distances and predecessors from source to every node."""
    if source not in graph:
        raise DijkstraError(f"source node '{source}' is not present in the graph")

    distances = {node: math.inf for node in graph}
    predecessors: dict[str, str | None] = {node: None for node in graph}
    distances[source] = 0.0
    queue: list[tuple[float, str]] = [(0.0, source)]

    while queue:
        current_distance, node = heapq.heappop(queue)
        if current_distance > distances[node]:
            continue

        for neighbor, weight in graph[node].items():
            candidate = current_distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                predecessors[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))

    return distances, predecessors


def reconstruct_path(
    node: str, source: str, distances: dict[str, float], predecessors: dict[str, str | None]
) -> list[str] | None:
    """Rebuild the path from source to node, or return None if unreachable."""
    if math.isinf(distances[node]):
        return None

    path = [node]
    while path[-1] != source:
        predecessor = predecessors[path[-1]]
        if predecessor is None:
            return None
        path.append(predecessor)

    return list(reversed(path))


def json_number(distance: float) -> int | float | None:
    """Render integral float distances as ints for cleaner JSON."""
    if math.isinf(distance):
        return None
    if distance.is_integer():
        return int(distance)
    return distance


def run(graph_uri: str, source: str) -> dict[str, Any]:
    graph = parse_graph(load_uri(graph_uri))
    distances, predecessors = shortest_paths(graph, source)

    return {
        "source": source,
        "distances": {
            node: json_number(distance) for node, distance in sorted(distances.items())
        },
        "paths": {
            node: reconstruct_path(node, source, distances, predecessors)
            for node in sorted(graph)
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Dijkstra's algorithm on a JSON adjacency graph loaded from a URI."
    )
    parser.add_argument("graph_uri", help="Graph URI or local path to a JSON adjacency graph")
    parser.add_argument("--source", required=True, help="Source node identifier")
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level for stdout output (default: 2)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = run(args.graph_uri, args.source)
    except DijkstraError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=args.indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
