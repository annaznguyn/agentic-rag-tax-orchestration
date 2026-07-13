"""Plot the embeddings stored in the PGVector collection as a 2D scatter chart.

Embeddings are high-dimensional, so they are reduced to 2 dimensions with PCA
before plotting. Points that sit close together in the chart are chunks whose
content is semantically similar.

Usage:
    python scripts/visualize_embeddings.py [--query "some question"]
"""

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import sqlalchemy
from dotenv import load_dotenv
from sklearn.decomposition import PCA

load_dotenv()

COLLECTION = "tax_orchestrator"
OUT_FILE = "embeddings_plot.png"


def fetch_embeddings() -> tuple[np.ndarray, list[dict]]:
    engine = sqlalchemy.create_engine(os.environ["DATABASE_URL"])
    query = sqlalchemy.text("""
        select e.embedding::text, e.document, e.cmetadata
        from langchain_pg_embedding e
        join langchain_pg_collection c on c.uuid = e.collection_id
        where c.name = :collection
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, {"collection": COLLECTION}).fetchall()

    vectors = np.array([json.loads(r[0]) for r in rows])
    metas = [{"document": r[1], **(r[2] or {})} for r in rows]
    return vectors, metas


def embed_query(text: str) -> np.ndarray:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    emb = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    return np.array(emb.embed_query(text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="optional query to plot alongside the chunks")
    args = parser.parse_args()

    vectors, metas = fetch_embeddings()
    print(f"fetched {len(vectors)} embeddings of dimension {vectors.shape[1]}")

    all_vectors = vectors
    if args.query:
        all_vectors = np.vstack([vectors, embed_query(args.query)])

    coords = PCA(n_components=2).fit_transform(all_vectors)
    chunk_coords = coords[: len(vectors)]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(chunk_coords[:, 0], chunk_coords[:, 1], s=120, color="#4c72b0", zorder=3)
    for (x, y), meta in zip(chunk_coords, metas):
        ax.annotate(
            str(meta.get("chunk_index", "?")),
            (x, y),
            textcoords="offset points",
            xytext=(8, 6),
            fontsize=11,
        )

    if args.query:
        qx, qy = coords[-1]
        ax.scatter([qx], [qy], s=200, color="#c44e52", marker="*", zorder=4)
        ax.annotate(
            f'query: "{args.query}"',
            (qx, qy),
            textcoords="offset points",
            xytext=(10, -14),
            fontsize=11,
            color="#c44e52",
        )

    title = metas[0].get("title", COLLECTION) if metas else COLLECTION
    ax.set_title(f"Embeddings of '{title}' chunks (PCA projection to 2D)")
    ax.set_xlabel("PCA component 1")
    ax.set_ylabel("PCA component 2")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_FILE, dpi=150)
    print(f"saved {OUT_FILE}")


if __name__ == "__main__":
    main()
