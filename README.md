# dijkstra

## Description

This project provides a standalone Python script, `dijkstra.py`, that runs
Dijkstra's algorithm on a directed weighted graph.

The graph is loaded from a URI and must be provided as a JSON adjacency object.
The script computes the shortest distances and paths from one source node to
all nodes in the graph.

Graph rules:

- Node identifiers must be strings.
- Edge weights must be numeric, finite, and non-negative.
- The graph is directed. For an undirected graph, include both directions.
- Unreachable nodes are included in the output with `null` distance and path.

## Build

No build step is required. Run the script with Python 3:

```sh
python3 dijkstra.py --help
```

The script supports local paths, `file://` URIs, and `http://` or `https://`
URLs using the Python standard library.

For broader URI scheme support, install optional `fsspec`:

```sh
pip install fsspec
```

## How to use

```sh
python3 dijkstra.py GRAPH_URI --source NODE [--indent N]
```

Arguments:

- `GRAPH_URI`: URI or local path to a JSON adjacency graph.
- `--source NODE`: required source node identifier.
- `--indent N`: optional JSON indentation level for output. The default is `2`.

Input graph format:

```json
{
  "A": {"B": 4, "C": 2},
  "B": {"C": 5, "D": 10},
  "C": {"B": 1, "D": 8},
  "D": {},
  "E": {}
}
```

Output format:

- `source`: the source node used for the run.
- `distances`: shortest distance from the source to each node.
- `paths`: shortest path from the source to each node.

## Examples

Create a graph file:

```sh
cat > graph.json <<'JSON'
{
  "A": {"B": 4, "C": 2},
  "B": {"C": 5, "D": 10},
  "C": {"B": 1, "D": 8},
  "D": {},
  "E": {}
}
JSON
```

Run Dijkstra from node `A` using a local path:

```sh
python3 dijkstra.py graph.json --source A
```

Run the same graph using a `file://` URI:

```sh
python3 dijkstra.py file://"$PWD"/graph.json --source A
```

Example output:

```json
{
  "distances": {
    "A": 0,
    "B": 3,
    "C": 2,
    "D": 10,
    "E": null
  },
  "paths": {
    "A": [
      "A"
    ],
    "B": [
      "A",
      "C",
      "B"
    ],
    "C": [
      "A",
      "C"
    ],
    "D": [
      "A",
      "C",
      "D"
    ],
    "E": null
  },
  "source": "A"
}
```

If the graph is invalid, the script prints an error to stderr and exits with a
non-zero status.
