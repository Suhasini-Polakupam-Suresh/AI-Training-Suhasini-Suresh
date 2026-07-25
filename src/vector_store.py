"""
Vector Store Module for Health Insurance AI Assistant
Manages ChromaDB vector database for semantic search
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class VectorStoreManager:
    """Manage ChromaDB vector store for health insurance documents"""
    
    def __init__(
        self, 
        persist_directory: str = "data/vectorstore",
        collection_name: str = "health_insurance",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Health insurance documents and FAQs"}
        )
        
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of document chunks with text and metadata
        """
        if not chunks:
            print("No chunks to add")
            return
        
        # Prepare data
        texts = [chunk['text'] for chunk in chunks]
        ids = [chunk['chunk_id'] for chunk in chunks]
        metadatas = [
            {
                'source': chunk['source'],
                'chunk_index': chunk['metadata']['chunk_index'],
                'total_chunks': chunk['metadata']['total_chunks']
            }
            for chunk in chunks
        ]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embed_texts(texts)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            
            self.collection.add(
                embeddings=embeddings[i:batch_end],
                documents=texts[i:batch_end],
                ids=ids[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            
            print(f"  Added batch {i//batch_size + 1} ({batch_end}/{len(texts)} chunks)")
        
        print(f"✓ Successfully added {len(texts)} chunks to vector store")
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Dict:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            Dictionary with documents, distances, and metadata
        """
        # Generate query embedding
        query_embedding = self.embed_texts([query])[0]
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict
        )
        
        return {
            'documents': results['documents'][0],
            'distances': results['distances'][0],
            'metadatas': results['metadatas'][0],
            'ids': results['ids'][0]
        }
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()
        
        # Get sample to analyze sources
        if count > 0:
            sample = self.collection.get(limit=count)
            sources = set(meta['source'] for meta in sample['metadatas'])
        else:
            sources = set()
        
        return {
            'total_documents': count,
            'unique_sources': len(sources),
            'sources': list(sources),
            'collection_name': self.collection_name
        }
    
    def clear_collection(self) -> None:
        """Clear all documents from collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Health insurance documents and FAQs"}
        )
        print("✓ Collection cleared")


def initialize_vector_store():
    """Initialize vector store with processed documents"""
    print("=" * 60)
    print("Vector Store Initialization")
    print("=" * 60)
    
    # Load processed chunks
    processed_file = Path("data/processed/processed_chunks.json")
    
    if not processed_file.exists():
        print("Error: Processed data not found. Run data_processing.py first.")
        return
    
    with open(processed_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} processed chunks")
    
    # Initialize vector store
    vector_store = VectorStoreManager()
    
    # Check if collection already has data
    stats = vector_store.get_collection_stats()
    if stats['total_documents'] > 0:
        print(f"\nWarning: Collection already contains {stats['total_documents']} documents")
        response = input("Clear existing data? (yes/no): ").strip().lower()
        if response == 'yes':
            vector_store.clear_collection()
    
    # Add documents
    print("\nAdding documents to vector store...")
    vector_store.add_documents(chunks)
    
    # Display statistics
    stats = vector_store.get_collection_stats()
    print("\nVector Store Statistics:")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Unique sources: {stats['unique_sources']}")
    print(f"  Sources:")
    for source in stats['sources']:
        print(f"    - {source}")
    
    # Test search
    print("\nTesting search functionality...")
    test_query = "What is a deductible?"
    results = vector_store.search(test_query, n_results=3)
    
    print(f"\nTest query: '{test_query}'")
    print(f"Found {len(results['documents'])} results:")
    for i, (doc, dist, meta) in enumerate(zip(results['documents'], results['distances'], results['metadatas'])):
        print(f"\n  Result {i+1} (distance: {dist:.4f}):")
        print(f"  Source: {meta['source']}")
        print(f"  Text: {doc[:150]}...")
    
    print("\n✓ Vector store initialization complete!")


def main():
    """Main execution function"""
    initialize_vector_store()


if __name__ == "__main__":
    main()
