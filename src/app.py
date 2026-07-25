"""
Streamlit Web Application for Health Insurance AI Assistant
Interactive demo interface
"""

import streamlit as st
import time
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_pipeline import HealthInsuranceRAG
from model_handler import OllamaModelHandler


# Page config
st.set_page_config(
    page_title="Health Insurance AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #f0fff0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #fff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_rag_pipeline(model_name: str):
    """Load and cache RAG pipeline"""
    try:
        return HealthInsuranceRAG(model_name=model_name, n_retrieval_results=3)
    except Exception as e:
        st.error(f"Error loading RAG pipeline: {e}")
        return None


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Health Insurance AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask me anything about health insurance policies, coverage, and claims</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        available_models = ['llama3', 'mistral', 'phi3']
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            index=0,
            help="Choose the LLM model for generating responses"
        )
        
        # Number of context documents
        n_docs = st.slider(
            "Context Documents",
            min_value=1,
            max_value=5,
            value=3,
            help="Number of relevant documents to retrieve"
        )
        
        st.divider()
        
        # About section
        st.header("ℹ️ About")
        st.markdown("""
        This AI assistant uses:
        - **RAG** (Retrieval Augmented Generation)
        - **Open-source LLMs** (via Ollama)
        - **ChromaDB** for vector search
        - **Semantic retrieval** for accurate context
        """)
        
        st.divider()
        
        # Example questions
        st.header("💡 Example Questions")
        example_questions = [
            "What is a deductible?",
            "How do I file a claim?",
            "What mental health services are covered?",
            "Difference between HMO and PPO?",
            "What are preventive care services?"
        ]
        
        for q in example_questions:
            if st.button(q, key=f"example_{q[:20]}", use_container_width=True):
                st.session_state.current_question = q
                st.rerun()
    
    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    
    # Load RAG pipeline
    with st.spinner("Loading AI model..."):
        rag = load_rag_pipeline(selected_model)
    
    if rag is None:
        st.error("❌ Failed to initialize RAG pipeline")
        st.info("""
        **Troubleshooting:**
        1. Make sure Ollama is running: `ollama serve`
        2. Install the model: `ollama pull llama3`
        3. Initialize vector store: `python src/vector_store.py`
        """)
        return
    
    # Update retrieval count if changed
    rag.n_retrieval_results = n_docs
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Ask Your Question")
        
        # Initialize session state for question
        if 'question_input' not in st.session_state:
            st.session_state.question_input = ""
        
        # Sync current_question to question_input when example button is clicked
        if 'current_question' in st.session_state and st.session_state.current_question:
            st.session_state.question_input = st.session_state.current_question
            st.session_state.current_question = ""
        
        question = st.text_area(
            "Type your question here:",
            height=100,
            placeholder="e.g., What is the difference between copay and coinsurance?",
            key="question_input"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
        with col_btn2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.session_state.history = []
            st.session_state.question_input = ""
            st.rerun()
        
        # Process question
        if ask_button and question.strip():
            
            with st.spinner("🤔 Thinking..."):
                start_time = time.time()
                
                # Get answer
                response = rag.answer_question(question, verbose=True)
                
                # Store in history
                st.session_state.history.insert(0, {
                    'question': question,
                    'answer': response['answer'],
                    'sources': response.get('context', {}).get('sources', []),
                    'timing': response['timing'],
                    'model': response['model']
                })
            
            # Display answer
            st.markdown("### 💡 Answer")
            st.markdown(f'<div class="answer-box">{response["answer"]}</div>', unsafe_allow_html=True)
            
            # Display metadata
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("⏱️ Total Time", f"{response['timing']['total']:.2f}s")
            with col_m2:
                st.metric("🔍 Retrieval", f"{response['timing']['retrieval']:.2f}s")
            with col_m3:
                st.metric("🤖 Generation", f"{response['timing']['generation']:.2f}s")
            
            # Display sources
            if 'context' in response and response['context']['sources']:
                st.markdown("### 📚 Sources")
                sources = list(set(response['context']['sources']))
                for source in sources:
                    st.markdown(f"- {source}")
    
    with col2:
        st.header("📊 Statistics")
        
        # Display stats
        try:
            stats = rag.vector_store.get_collection_stats()
            st.metric("Total Documents", stats['total_documents'])
            st.metric("Unique Sources", stats['unique_sources'])
            st.metric("Model", selected_model)
            st.metric("Context Docs", n_docs)
        except Exception as e:
            st.error(f"Error loading stats: {e}")
    
    # History section
    if st.session_state.history:
        st.divider()
        st.header("📜 Recent Questions")
        
        for i, item in enumerate(st.session_state.history[:5]):
            with st.expander(f"Q: {item['question'][:80]}...", expanded=(i==0)):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Answer:** {item['answer']}")
                st.markdown(f"**Model:** {item['model']}")
                st.markdown(f"**Time:** {item['timing']['total']:.2f}s")
                if item['sources']:
                    st.markdown(f"**Sources:** {', '.join(set(item['sources']))}")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Health Insurance AI Assistant | Capstone Project | July 2026</p>
        <p>Powered by Open-Source LLMs via Ollama 🦙</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
