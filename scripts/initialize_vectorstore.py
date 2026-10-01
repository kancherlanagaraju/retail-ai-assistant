#!/usr/bin/env python3
"""
Initialize the vector store on application startup.
This ensures the ChromaDB is populated with documents on first run.
"""

import logging
from pathlib import Path
from vectorstore.db_builder import initialize_and_populate_vectorstore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_vectorstore_initialized():
    """Initialize vector store if it hasn't been initialized yet."""
    db_path = Path("./vectorstore/chroma_db")

    # Check if the vector store already has documents
    if db_path.exists():
        try:
            from vectorstore.db_builder import VectorStoreBuilder
            builder = VectorStoreBuilder()
            stats = builder.get_collection_stats()

            if stats.get('total_documents', 0) > 0:
                logger.info(f"✓ Vector store already initialized with {stats['total_documents']} documents")
                return
        except Exception as e:
            logger.warning(f"Could not check vector store: {str(e)}")

    # Initialize and populate the vector store
    logger.info("Initializing vector store...")
    try:
        initialize_and_populate_vectorstore()
        logger.info("✓ Vector store initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {str(e)}")
        raise


if __name__ == "__main__":
    ensure_vectorstore_initialized()
