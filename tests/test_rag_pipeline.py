"""
Unit Tests for RAG Pipeline
Tests core functionality of the Health Insurance AI Assistant
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_processing import HealthInsuranceDataProcessor
from vector_store import VectorStoreManager


class TestDataProcessing:
    """Test data processing module"""
    
    def test_chunk_text_basic(self):
        """Test basic text chunking"""
        processor = HealthInsuranceDataProcessor()
        text = "This is a test. " * 50  # Create text > chunk_size
        
        chunks = processor.chunk_text(text, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1, "Should create multiple chunks"
        assert all(len(chunk) <= 120 for chunk in chunks), "Chunks should respect size limit"
    
    def test_chunk_text_empty(self):
        """Test chunking empty text"""
        processor = HealthInsuranceDataProcessor()
        chunks = processor.chunk_text("")
        
        assert chunks == [], "Empty text should return empty list"
    
    def test_chunk_text_short(self):
        """Test chunking text shorter than chunk_size"""
        processor = HealthInsuranceDataProcessor()
        text = "Short text."
        
        chunks = processor.chunk_text(text, chunk_size=100)
        
        assert len(chunks) == 1, "Short text should create single chunk"
        assert chunks[0] == text, "Short text should be unchanged"
    
    def test_create_sample_data(self):
        """Test sample data creation"""
        import tempfile
        import shutil
        
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            processor = HealthInsuranceDataProcessor(
                raw_data_path=str(temp_dir / "raw"),
                processed_data_path=str(temp_dir / "processed")
            )
            
            processor.create_sample_data()
            
            # Check files created
            json_files = list((temp_dir / "raw").glob("*.json"))
            assert len(json_files) > 0, "Should create sample JSON files"
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)
    
    def test_process_documents(self):
        """Test document processing"""
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            processor = HealthInsuranceDataProcessor(
                raw_data_path=str(temp_dir / "raw"),
                processed_data_path=str(temp_dir / "processed")
            )
            
            # Create and process data
            processor.create_sample_data()
            chunks = processor.process_documents()
            
            # Verify chunks
            assert len(chunks) > 0, "Should process documents into chunks"
            assert all('text' in chunk for chunk in chunks), "All chunks should have text"
            assert all('source' in chunk for chunk in chunks), "All chunks should have source"
            assert all('chunk_id' in chunk for chunk in chunks), "All chunks should have ID"
            
        finally:
            shutil.rmtree(temp_dir)


class TestVectorStore:
    """Test vector store module"""
    
    def test_embed_texts(self):
        """Test text embedding generation"""
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            vector_store = VectorStoreManager(persist_directory=str(temp_dir))
            
            texts = ["This is a test", "Another test sentence"]
            embeddings = vector_store.embed_texts(texts)
            
            assert len(embeddings) == len(texts), "Should generate embedding for each text"
            assert all(isinstance(emb, list) for emb in embeddings), "Embeddings should be lists"
            assert all(len(emb) > 0 for emb in embeddings), "Embeddings should not be empty"
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_add_and_search_documents(self):
        """Test adding documents and searching"""
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            vector_store = VectorStoreManager(persist_directory=str(temp_dir))
            
            # Create test chunks
            chunks = [
                {
                    'text': 'A deductible is the amount you pay before insurance covers costs.',
                    'source': 'Test Document',
                    'chunk_id': 'test_chunk_1',
                    'metadata': {
                        'chunk_index': 0,
                        'total_chunks': 1
                    }
                }
            ]
            
            # Add documents
            vector_store.add_documents(chunks)
            
            # Search
            results = vector_store.search("What is a deductible?", n_results=1)
            
            assert len(results['documents']) > 0, "Search should return results"
            assert 'deductible' in results['documents'][0].lower(), "Result should contain query term"
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_collection_stats(self):
        """Test collection statistics"""
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            vector_store = VectorStoreManager(persist_directory=str(temp_dir))
            
            stats = vector_store.get_collection_stats()
            
            assert 'total_documents' in stats, "Stats should include document count"
            assert 'unique_sources' in stats, "Stats should include source count"
            assert stats['total_documents'] == 0, "New collection should be empty"
            
        finally:
            shutil.rmtree(temp_dir)


class TestRAGIntegration:
    """Integration tests for RAG pipeline"""
    
    @pytest.mark.slow
    def test_end_to_end_qa(self):
        """Test complete question-answering flow"""
        # This test requires Ollama running with llama3
        # Mark as slow test, skip in quick test runs
        
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Setup
            from data_processing import HealthInsuranceDataProcessor
            from vector_store import VectorStoreManager
            
            processor = HealthInsuranceDataProcessor(
                raw_data_path=str(temp_dir / "raw"),
                processed_data_path=str(temp_dir / "processed")
            )
            
            # Process data
            processor.create_sample_data()
            chunks = processor.process_documents()
            
            # Create vector store
            vector_store = VectorStoreManager(persist_directory=str(temp_dir / "vectorstore"))
            vector_store.add_documents(chunks)
            
            # Test retrieval
            results = vector_store.search("What is a deductible?", n_results=3)
            
            assert len(results['documents']) == 3, "Should retrieve 3 documents"
            assert any('deductible' in doc.lower() for doc in results['documents']), \
                "Results should be relevant to query"
            
            # Note: Testing model generation requires Ollama running
            # Skip if not available
            
        finally:
            shutil.rmtree(temp_dir)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_query(self):
        """Test handling of empty query"""
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            vector_store = VectorStoreManager(persist_directory=str(temp_dir))
            
            # Empty query should not crash
            results = vector_store.search("", n_results=1)
            
            # Should return some structure (even if empty)
            assert 'documents' in results
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_large_n_results(self):
        """Test requesting more results than available"""
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            vector_store = VectorStoreManager(persist_directory=str(temp_dir))
            
            # Add one document
            chunks = [
                {
                    'text': 'Test document',
                    'source': 'Test',
                    'chunk_id': 'test_1',
                    'metadata': {'chunk_index': 0, 'total_chunks': 1}
                }
            ]
            vector_store.add_documents(chunks)
            
            # Request more results than available
            results = vector_store.search("test", n_results=10)
            
            # Should return available documents without error
            assert len(results['documents']) <= 10
            
        finally:
            shutil.rmtree(temp_dir)


# Test configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])
