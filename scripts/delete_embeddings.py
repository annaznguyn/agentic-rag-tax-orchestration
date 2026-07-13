"""Delete all embeddings stored in the PGVector collection on Supabase.

Usage:
    python scripts/delete_embeddings.py          # asks for confirmation
    python scripts/delete_embeddings.py --yes    # skips confirmation
"""

import argparse
import os

import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

COLLECTION = "tax_orchestrator"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = parser.parse_args()

    engine = sqlalchemy.create_engine(os.environ["DATABASE_URL"])

    with engine.begin() as conn:
        count = conn.execute(
            sqlalchemy.text("""
                select count(*)
                from langchain_pg_embedding e
                join langchain_pg_collection c on c.uuid = e.collection_id
                where c.name = :collection
            """),
            {"collection": COLLECTION},
        ).scalar()

        if count == 0:
            print(f"collection '{COLLECTION}' has no embeddings, nothing to delete")
            return

        if not args.yes:
            answer = input(f"delete all {count} embeddings in '{COLLECTION}'? [y/N] ")
            if answer.strip().lower() not in ("y", "yes"):
                print("aborted")
                return

        deleted = conn.execute(
            sqlalchemy.text("""
                delete from langchain_pg_embedding e
                using langchain_pg_collection c
                where c.uuid = e.collection_id and c.name = :collection
            """),
            {"collection": COLLECTION},
        ).rowcount

    print(f"deleted {deleted} embeddings from '{COLLECTION}'")


if __name__ == "__main__":
    main()
