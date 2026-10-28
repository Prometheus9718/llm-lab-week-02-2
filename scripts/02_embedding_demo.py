"""Turn three short English sentences into vectors using local Ollama."""
from __future__ import annotations

import argparse
import json
import math
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from lab_common import ROOT, write_json


def cosine(a: list[float], b: list[float]) -> float:
    denominator = math.sqrt(sum(x*x for x in a) * sum(y*y for y in b))
    return sum(x*y for x, y in zip(a, b)) / denominator if denominator else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="all-minilm:22m")
    parser.add_argument("--url", default="http://localhost:11434")
    args = parser.parse_args()
    sentences = [
        "A cat is sleeping on a chair.",
        "A kitten is resting on a seat.",
        "A database stores customer transactions.",
    ]
    inputs = ["search_document: " + text for text in sentences] if args.model.startswith("nomic-embed-text") else sentences
    payload = json.dumps({"model": args.model, "input": inputs, "truncate": False}).encode("utf-8")
    request = Request(args.url.rstrip("/") + "/api/embed", data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=180) as response:
            result = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Ollama HTTP {exc.code}: {detail}\nCheck ollama list and the selected model.") from exc
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot call Ollama: {exc}\nKeep Ollama running; retry after the network/server is ready.") from exc
    vectors = result.get("embeddings", [])
    if len(vectors) != len(sentences) or not vectors[0]:
        raise SystemExit(f"Unexpected Ollama response: {list(result)}")
    dimensions = len(vectors[0])
    if any(len(vector) != dimensions for vector in vectors):
        raise SystemExit("Ollama returned vectors with inconsistent dimensions.")
    print("Model:", args.model)
    print("Dimensions:", dimensions)
    print("First 8 values:", vectors[0][:8])
    for index, sentence in enumerate(sentences, 1):
        print(f"Sentence {index}: {sentence}")
    print("Cosine similarity 1 vs 2:", round(cosine(vectors[0], vectors[1]), 4))
    print("Cosine similarity 1 vs 3:", round(cosine(vectors[0], vectors[2]), 4))
    print("Scores illustrate this example; they are not an accuracy benchmark.")
    output = ROOT / "data" / "demo" / "embedding-demo.json"
    write_json(output, {"model": args.model, "sentences": sentences, "dimensions": dimensions, "vectors": vectors})
    print("Saved:", output)


if __name__ == "__main__":
    main()
