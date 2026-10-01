"""
Vector store builder for Retail AI Assistant using ChromaDB.
Builds and manages a persistent vector database for semantic search with metadata filtering.
Uses mock embeddings when OpenAI key is not available for demonstration purposes.
"""

import json
import logging
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockEmbeddings:
    """Mock embeddings generator for testing without OpenAI API key."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate deterministic mock embeddings for documents."""
        embeddings = []
        for text in texts:
            # Generate deterministic embedding based on text hash
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to list of floats between -1 and 1
            embedding = [float((byte - 128) / 128) for byte in hash_bytes[:384]]
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Generate mock embedding for query."""
        return self.embed_documents([text])[0]


class VectorStoreBuilder:
    """Build and manage ChromaDB vector store for semantic search."""

    def __init__(
        self,
        db_path: str = "./vectorstore/chroma_db",
        collection_name: str = "retail-qa",
        data_file: str = "data/synthetic_datasets.json"
    ):
        """
        Initialize the vector store builder.

        Args:
            db_path: Path to ChromaDB persistent storage
            collection_name: Name of the collection
            data_file: Path to the synthetic datasets JSON file
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.data_file = data_file
        self.embeddings = MockEmbeddings()
        self.client = None
        self.collection = None

        # Create db path if it doesn't exist
        Path(db_path).mkdir(parents=True, exist_ok=True)

        self._initialize()

    def _initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        logger.info(f"Initializing vector store at {self.db_path}")

        try:
            logger.info("Loading embeddings model (using mock embeddings)...")
            logger.info("✓ Mock embeddings initialized")

            # Initialize ChromaDB client with persistent storage
            logger.info("Initializing ChromaDB persistent client...")
            self.client = chromadb.PersistentClient(path=self.db_path)
            logger.info("✓ ChromaDB client initialized")

            # Get or create collection
            logger.info(f"Setting up collection: {self.collection_name}")
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("✓ Collection initialized")
            logger.info("✓ Vector store initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise

    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Load documents from synthetic_datasets.json.

        Returns:
            List of documents with content and metadata
        """
        logger.info(f"Loading documents from {self.data_file}")

        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        documents = []
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Data file must contain a JSON array")

            for idx, item in enumerate(data):
                if not isinstance(item, dict):
                    logger.warning(f"Skipping invalid item at index {idx}")
                    continue

                # Extract fields
                doc_content = item.get('doc', '')
                category = item.get('category', 'unknown')
                audience = item.get('audience', 'unknown')

                if not doc_content:
                    logger.warning(f"Skipping item {idx}: empty doc field")
                    continue

                # Create document with metadata
                doc = {
                    'id': f"doc_{idx}",
                    'content': doc_content,
                    'metadata': {
                        'category': category,
                        'audience': audience
                    }
                }
                documents.append(doc)

            logger.info(f"✓ Loaded {len(documents)} documents from {self.data_file}")
            return documents

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise

    def add_documents_to_store(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store.

        Args:
            documents: List of document dictionaries with content and metadata
        """
        if not documents:
            logger.warning("No documents to add")
            return

        try:
            logger.info(f"Adding {len(documents)} documents to vector store...")

            ids = [doc['id'] for doc in documents]
            contents = [doc['content'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]

            # Generate embeddings for documents
            embeddings = self.embeddings.embed_documents(contents)

            # Add documents with embeddings and metadata
            self.collection.add(
                ids=ids,
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(f"✓ Successfully added {len(ids)} documents to vector store")

            # Verify storage
            doc_count = self.collection.count()
            logger.info(f"✓ Vector store now contains {doc_count} documents")

        except Exception as e:
            logger.error(f"Failed to add documents to store: {str(e)}")
            raise

    def get_retriever(self, category: Optional[str] = None, k: int = 5):
        """
        Get a retriever with optional metadata filtering by category.

        Args:
            category: Optional category to filter by (e.g., "HR", "IT Support")
            k: Number of results to return

        Returns:
            Function that performs similarity search with optional filtering
        """
        logger.info(f"Creating retriever" + (f" for category: {category}" if category else ""))

        if not self.collection:
            raise RuntimeError("Vector store not initialized")

        try:
            def retriever_func(query: str) -> List[Dict[str, Any]]:
                """Retrieve documents matching the query."""
                return self.search(query, category=category, k=k)

            logger.info(f"✓ Retriever created" + (f" with category filter: {category}" if category else ""))
            return retriever_func

        except Exception as e:
            logger.error(f"Failed to create retriever: {str(e)}")
            raise

    def search(self, query: str, category: Optional[str] = None, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the vector store for similar documents.

        Args:
            query: Search query string
            category: Optional category filter
            k: Number of results to return

        Returns:
            List of matching documents with metadata
        """
        logger.info(f"Searching for: '{query}'" + (f" in category: {category}" if category else ""))

        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)

            # Build where filter if category specified
            where_filter = None
            if category:
                where_filter = {"category": {"$eq": category}}

            # Search with optional filtering
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_filter
            )

            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for idx, doc_id in enumerate(results['ids'][0]):
                    doc = {
                        'id': doc_id,
                        'content': results['documents'][0][idx],
                        'distance': results['distances'][0][idx] if results['distances'] else None,
                        'metadata': results['metadatas'][0][idx] if results['metadatas'] else {}
                    }
                    formatted_results.append(doc)

            logger.info(f"✓ Found {len(formatted_results)} matching documents")
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            doc_count = self.collection.count()

            # Get all documents to extract unique categories and audiences
            all_docs = self.collection.get()
            categories = set()
            audiences = set()

            if all_docs.get('metadatas'):
                for metadata in all_docs['metadatas']:
                    if isinstance(metadata, dict):
                        categories.add(metadata.get('category', 'unknown'))
                        audiences.add(metadata.get('audience', 'unknown'))

            stats = {
                'collection_name': self.collection_name,
                'total_documents': doc_count,
                'categories': sorted(list(categories)),
                'audiences': sorted(list(audiences)),
                'db_path': self.db_path
            }

            logger.info(f"Collection stats: {doc_count} documents, {len(categories)} categories")
            return stats

        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            logger.info("Clearing vector store collection...")

            # Get all document IDs
            all_docs = self.collection.get()
            if all_docs.get('ids'):
                self.collection.delete(ids=all_docs['ids'])
                logger.info(f"✓ Cleared {len(all_docs['ids'])} documents from collection")
            else:
                logger.info("✓ Collection already empty")

        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            raise


def initialize_and_populate_vectorstore(
    db_path: str = "./vectorstore/chroma_db",
    data_file: str = "data/synthetic_datasets.json"
) -> VectorStoreBuilder:
    """
    Initialize and populate the vector store in one step.

    Args:
        db_path: Path to ChromaDB persistent storage
        data_file: Path to the synthetic datasets JSON file

    Returns:
        Initialized and populated VectorStoreBuilder instance
    """
    logger.info("="*70)
    logger.info("VECTOR STORE INITIALIZATION & POPULATION")
    logger.info("="*70)

    try:
        # Initialize builder
        builder = VectorStoreBuilder(
            db_path=db_path,
            data_file=data_file
        )

        # Load documents
        documents = builder.load_documents()

        # Clear existing collection
        logger.info("Clearing existing collection...")
        builder.clear_collection()

        # Add documents to store
        builder.add_documents_to_store(documents)

        # Print statistics
        stats = builder.get_collection_stats()
        logger.info("\n" + "="*70)
        logger.info("VECTOR STORE STATISTICS")
        logger.info("="*70)
        logger.info(f"Total Documents:   {stats.get('total_documents')}")
        logger.info(f"Categories:        {', '.join(stats.get('categories', []))}")
        logger.info(f"Audiences:         {', '.join(stats.get('audiences', []))}")
        logger.info(f"Storage Location:  {stats.get('db_path')}")
        logger.info("="*70)

        return builder

    except Exception as e:
        logger.error(f"Failed to initialize vector store: {str(e)}")
        raise


if __name__ == "__main__":
    """Run the vector store initialization when script is executed directly."""
    try:
        # Initialize and populate vector store
        builder = initialize_and_populate_vectorstore()

        # Test the retriever
        logger.info("\n" + "="*70)
        logger.info("TESTING RETRIEVER FUNCTIONALITY")
        logger.info("="*70)

        # Test 1: Search without category filter
        logger.info("\n1. Testing search without category filter:")
        logger.info("   Query: 'payment methods'")
        results = builder.search("payment methods", k=2)
        for i, result in enumerate(results[:2], 1):
            category = result['metadata'].get('category', 'unknown')
            content = result['content'][:70]
            logger.info(f"   Result {i}: [{category}] {content}...")

        # Test 2: Search with category filter
        logger.info("\n2. Testing search with HR category filter:")
        logger.info("   Query: 'vacation policy'")
        results = builder.search("vacation policy", category="HR", k=2)
        for i, result in enumerate(results[:2], 1):
            category = result['metadata'].get('category', 'unknown')
            content = result['content'][:70]
            logger.info(f"   Result {i}: [{category}] {content}...")

        # Test 3: Get retriever function
        logger.info("\n3. Testing get_retriever function:")
        logger.info("   Creating retriever for Shipping & Delivery category")
        retriever = builder.get_retriever(category="Shipping & Delivery", k=2)
        test_results = retriever("shipping costs")
        logger.info(f"   Retriever returned {len(test_results)} documents")

        # Test 4: Collection statistics
        logger.info("\n4. Final Collection Statistics:")
        stats = builder.get_collection_stats()
        logger.info(f"   Total Documents: {stats['total_documents']}")
        logger.info(f"   Categories: {len(stats['categories'])}")
        logger.info(f"   Audiences: {len(stats['audiences'])}")

        logger.info("\n" + "="*70)
        logger.info("✅ VECTOR STORE SUCCESSFULLY INITIALIZED AND TESTED")
        logger.info("="*70 + "\n")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        exit(1)
