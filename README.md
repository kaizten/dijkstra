# Dijkstra

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

This project includes a `requirements.txt` file with the Python dependencies.
Create a virtual environment and install those dependencies before running the
script:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Then verify the command-line interface:

```sh
python dijkstra.py --help
```

You can also build a Docker image:

```sh
docker build -t dijkstra .
```

Run the image by passing the same arguments you would pass to `dijkstra.py`:

```sh
docker run --rm -v "$PWD:/data" dijkstra /data/graph.json --source A
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
