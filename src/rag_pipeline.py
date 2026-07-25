"""
RAG Pipeline Module for Health Insurance AI Assistant
Combines retrieval and generation for question answering
"""

import time
from typing import List, Dict, Optional, Tuple
from vector_store import VectorStoreManager
from model_handler import OllamaModelHandler


class HealthInsuranceRAG:
    """Complete RAG pipeline for health insurance queries"""
    
    def __init__(
        self,
        model_name: str = 'llama3',
        n_retrieval_results: int = 3,
        vector_store_path: str = "data/vectorstore"
    ):
        """
        Initialize RAG pipeline
        
        Args:
            model_name: Ollama model to use
            n_retrieval_results: Number of documents to retrieve
            vector_store_path: Path to ChromaDB store
        """
        print("Initializing RAG Pipeline...")
        
        # Initialize components
        self.vector_store = VectorStoreManager(persist_directory=vector_store_path)
        self.model_handler = OllamaModelHandler(model_name=model_name)
        self.n_retrieval_results = n_retrieval_results
        
        # System prompt for health insurance domain
        self.system_prompt = """You are an expert health insurance advisor assistant.
Your role is to help users understand health insurance concepts, policies, coverage, and claims processes.

Guidelines:
- Answer based on the provided context
- If the context doesn't contain enough information, acknowledge this
- Explain technical terms in simple language
- Be concise but thorough
- Provide specific examples when helpful
- If discussing costs, remind users that actual amounts vary by plan"""
        
        print("✓ RAG Pipeline ready")
    
    def retrieve_context(self, query: str) -> Tuple[List[str], List[Dict]]:
        """
        Retrieve relevant context documents
        
        Args:
            query: User query
            
        Returns:
            Tuple of (documents, metadata)
        """
        results = self.vector_store.search(
            query=query,
            n_results=self.n_retrieval_results
        )
        
        return results['documents'], results['metadatas']
    
    def answer_question(
        self,
        question: str,
        verbose: bool = False
    ) -> Dict:
        """
        Answer a question using RAG pipeline
        
        Args:
            question: User question
            verbose: Whether to return detailed information
            
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        
        # Step 1: Retrieve relevant context
        retrieval_start = time.time()
        context_docs, context_metadata = self.retrieve_context(question)
        retrieval_time = time.time() - retrieval_start
        
        # Step 2: Generate answer with context
        generation_start = time.time()
        result = self.model_handler.generate_with_context(
            query=question,
            context_documents=context_docs,
            system_prompt=self.system_prompt
        )
        generation_time = time.time() - generation_start
        
        total_time = time.time() - start_time
        
        # Build response
        response = {
            'question': question,
            'answer': result.get('response', 'Error generating response'),
            'model': result.get('model', self.model_handler.model_name),
            'timing': {
                'total': total_time,
                'retrieval': retrieval_time,
                'generation': generation_time
            }
        }
        
        # Add verbose information
        if verbose:
            response['context'] = {
                'documents': context_docs,
                'sources': [meta['source'] for meta in context_metadata],
                'num_docs': len(context_docs)
            }
            response['model_stats'] = {
                'latency': result.get('latency', 0),
                'eval_count': result.get('eval_count', 0)
            }
        
        return response
    
    def batch_answer(self, questions: List[str]) -> List[Dict]:
        """
        Answer multiple questions
        
        Args:
            questions: List of questions
            
        Returns:
            List of responses
        """
        responses = []
        for i, question in enumerate(questions):
            print(f"\nProcessing question {i+1}/{len(questions)}...")
            response = self.answer_question(question)
            responses.append(response)
        
        return responses
    
    def evaluate_answer_quality(self, question: str, answer: str) -> Dict:
        """
        Simple evaluation of answer quality
        
        Args:
            question: Original question
            answer: Generated answer
            
        Returns:
            Dictionary with quality metrics
        """
        # Basic metrics
        metrics = {
            'answer_length': len(answer),
            'is_empty': len(answer.strip()) == 0,
            'has_uncertainty': any(phrase in answer.lower() for phrase in [
                "i don't know", "not sure", "unclear", "cannot answer"
            ]),
            'has_technical_terms': any(term in answer.lower() for term in [
                'deductible', 'premium', 'copay', 'coinsurance', 'hmo', 'ppo'
            ])
        }
        
        # Simple quality score (0-100)
        score = 100
        if metrics['is_empty']:
            score = 0
        elif metrics['has_uncertainty']:
            score -= 30
        if metrics['answer_length'] < 50:
            score -= 20
        elif metrics['answer_length'] > 500:
            score -= 10
        
        metrics['quality_score'] = max(0, score)
        
        return metrics


def interactive_mode():
    """Run interactive Q&A session"""
    print("=" * 60)
    print("Health Insurance AI Assistant - Interactive Mode")
    print("=" * 60)
    print("\nInitializing...")
    
    try:
        rag = HealthInsuranceRAG(model_name='llama3')
    except Exception as e:
        print(f"\n❌ Error initializing RAG pipeline: {e}")
        print("\nMake sure:")
        print("  1. Ollama is running: ollama serve")
        print("  2. Model is installed: ollama pull llama3")
        print("  3. Vector store is initialized: python src/vector_store.py")
        return
    
    print("\n✓ Ready! Ask me anything about health insurance.")
    print("  Type 'quit' or 'exit' to end the session")
    print("  Type 'examples' to see sample questions\n")
    
    example_questions = [
        "What is a deductible?",
        "How do I file a claim for an emergency room visit?",
        "What mental health services are covered?",
        "What is the difference between copay and coinsurance?",
        "What preventive care services are free?"
    ]
    
    while True:
        try:
            # Get user input
            user_input = input("\n❓ Your question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for using Health Insurance AI Assistant!")
                break
            
            if user_input.lower() == 'examples':
                print("\nExample questions:")
                for i, q in enumerate(example_questions, 1):
                    print(f"  {i}. {q}")
                continue
            
            # Process question
            print("\n🔍 Searching knowledge base...")
            response = rag.answer_question(user_input, verbose=True)
            
            # Display answer
            print(f"\n💡 Answer:\n{response['answer']}")
            
            # Display sources
            if 'context' in response:
                print(f"\n📚 Sources: {', '.join(set(response['context']['sources']))}")
            
            # Display timing
            print(f"\n⏱️  Response time: {response['timing']['total']:.2f}s")
            print(f"   (Retrieval: {response['timing']['retrieval']:.2f}s, "
                  f"Generation: {response['timing']['generation']:.2f}s)")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def demo_mode():
    """Run demo with predefined questions"""
    print("=" * 60)
    print("Health Insurance AI Assistant - Demo Mode")
    print("=" * 60)
    
    # Initialize RAG
    print("\nInitializing RAG pipeline...")
    rag = HealthInsuranceRAG(model_name='llama3')
    
    # Demo questions
    demo_questions = [
        "What is a deductible and how does it work?",
        "What mental health services does my insurance cover?",
        "How do I file a claim for an emergency room visit?",
        "What is the difference between HMO and PPO?",
        "Are preventive care services free?"
    ]
    
    print(f"\nRunning demo with {len(demo_questions)} questions...\n")
    
    for i, question in enumerate(demo_questions, 1):
        print("=" * 60)
        print(f"Question {i}/{len(demo_questions)}")
        print("=" * 60)
        print(f"❓ {question}\n")
        
        response = rag.answer_question(question, verbose=True)
        
        print(f"💡 Answer:\n{response['answer']}\n")
        print(f"📚 Sources: {', '.join(set(response['context']['sources']))}")
        print(f"⏱️  Time: {response['timing']['total']:.2f}s\n")
        
        time.sleep(1)  # Brief pause between questions
    
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
