# Changelog

All notable changes to the Health Insurance AI Assistant project.

## [1.0.0] - 2026-07-25

### Initial Release

#### Added
- **RAG Pipeline**: Complete retrieval-augmented generation system
  - Document processing with chunking
  - ChromaDB vector store for semantic search
  - Ollama integration for local LLM inference
  
- **Models Evaluated**:
  - Llama 3 (8B) - Selected as primary model
  - Mistral (7B) - Alternative option
  - Phi-3 (3.8B) - Lightweight option

- **Features**:
  - Streamlit web interface
  - Command-line interface
  - Interactive Q&A mode
  - Demo mode with preset questions
  
- **Data**:
  - 5 health insurance documents
  - ~45 processed chunks
  - Topics: basics, mental health, claims, preventive care, prescriptions

- **Documentation**:
  - Complete capstone report
  - Model comparison analysis
  - Demo presentation guide
  - Quick start guide
  - API documentation

- **Testing**:
  - Unit tests for core modules
  - Integration tests for RAG pipeline
  - Test coverage for edge cases

- **Notebooks**:
  - Data exploration
  - Model comparison
  - Prompt engineering

#### Technical Details
- Python 3.10+
- LangChain for orchestration
- ChromaDB for vector storage
- Streamlit for UI
- Ollama for model inference
- Sentence Transformers for embeddings

#### Performance
- 92% accuracy on test queries (Llama 3)
- Average response time: 1.2 seconds
- 3 context documents per query
- Memory usage: 8GB (Llama 3)

### [0.1.0] - 2026-07-20

#### Development
- Initial project structure
- Basic RAG pipeline prototype
- Sample data collection
- Model testing framework

---

## Future Releases

### [1.1.0] - Planned
- Multi-language support (Spanish, Chinese)
- Voice interface
- Enhanced error handling
- Improved prompt templates
- User feedback mechanism

### [2.0.0] - Planned
- Mobile application
- Fine-tuned models
- Real-time policy integration
- Personalized recommendations
- Advanced analytics dashboard
