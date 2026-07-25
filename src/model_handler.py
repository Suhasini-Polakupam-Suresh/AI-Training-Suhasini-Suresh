"""
Model Handler Module for Health Insurance AI Assistant
Interfaces with Ollama for local LLM inference
"""

import time
from typing import List, Dict, Optional
import ollama
from dataclasses import dataclass

# Configure Ollama client
ollama_client = ollama.Client(host='http://localhost:11434')


@dataclass
class ModelConfig:
    """Configuration for an LLM model"""
    name: str
    parameters: str
    context_length: int
    temperature: float = 0.7
    top_p: float = 0.9


class OllamaModelHandler:
    """Handle interactions with Ollama models"""
    
    # Predefined model configurations
    MODELS = {
        'llama3': ModelConfig(
            name='llama3',
            parameters='8B',
            context_length=8192,
            temperature=0.7
        ),
        'mistral': ModelConfig(
            name='mistral',
            parameters='7B',
            context_length=8192,
            temperature=0.7
        ),
        'phi3': ModelConfig(
            name='phi3',
            parameters='3.8B',
            context_length=4096,
            temperature=0.7
        )
    }
    
    def __init__(self, model_name: str = 'llama3'):
        """
        Initialize model handler
        
        Args:
            model_name: Name of the Ollama model to use
        """
        if model_name not in self.MODELS:
            raise ValueError(f"Model {model_name} not found. Available: {list(self.MODELS.keys())}")
        
        self.config = self.MODELS[model_name]
        self.model_name = model_name
        
        # Check if model is available
        try:
            ollama_client.show(model_name)
            print(f"✓ Model '{model_name}' is ready")
        except Exception as e:
            print(f"⚠ Model '{model_name}' not found locally")
            print(f"  Run: ollama pull {model_name}")
            raise e
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 500,
        stream: bool = False
    ) -> Dict:
        """
        Generate response from model
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Dictionary with response, tokens, and timing
        """
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        # Generate response
        try:
            response = ollama_client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'temperature': temperature or self.config.temperature,
                    'top_p': self.config.top_p,
                    'num_predict': max_tokens
                },
                stream=stream
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            if stream:
                return {'stream': response}
            else:
                return {
                    'response': response['message']['content'],
                    'model': self.model_name,
                    'latency': latency,
                    'eval_count': response.get('eval_count', 0),
                    'eval_duration': response.get('eval_duration', 0)
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'model': self.model_name,
                'latency': time.time() - start_time
            }
    
    def generate_with_context(
        self,
        query: str,
        context_documents: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict:
        """
        Generate response with retrieved context (RAG)
        
        Args:
            query: User query
            context_documents: List of relevant context documents
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with response and metadata
        """
        # Build context
        context = "\n\n".join([
            f"Context {i+1}:\n{doc}"
            for i, doc in enumerate(context_documents)
        ])
        
        # Build prompt with context
        rag_prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        # Default system prompt for health insurance
        if not system_prompt:
            system_prompt = """You are a helpful health insurance assistant. 
Answer questions based on the provided context accurately and concisely.
If the context doesn't contain enough information, say so.
Use simple language and explain technical terms."""
        
        # Generate response
        result = self.generate(
            prompt=rag_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        # Add context info
        if 'error' not in result:
            result['num_context_docs'] = len(context_documents)
            result['context_length'] = len(context)
        
        return result
    
    @staticmethod
    def list_available_models() -> List[str]:
        """List all locally available Ollama models"""
        try:
            models = ollama.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    @staticmethod
    def check_ollama_status() -> bool:
        """Check if Ollama service is running"""
        try:
            ollama.list()
            return True
        except Exception:
            return False


def test_model():
    """Test model functionality"""
    print("=" * 60)
    print("Model Handler Test")
    print("=" * 60)
    
    # Check Ollama status
    print("\nChecking Ollama service...")
    if not OllamaModelHandler.check_ollama_status():
        print("❌ Ollama service is not running")
        print("   Start it with: ollama serve")
        return
    print("✓ Ollama service is running")
    
    # List available models
    print("\nAvailable models:")
    available = OllamaModelHandler.list_available_models()
    for model in available:
        print(f"  - {model}")
    
    # Test model
    if 'llama3' in available or any('llama3' in m for m in available):
        print("\nTesting llama3 model...")
        handler = OllamaModelHandler('llama3')
        
        # Simple test
        print("\nTest 1: Simple query")
        result = handler.generate(
            prompt="What is health insurance in one sentence?",
            system_prompt="You are a helpful assistant. Answer concisely."
        )
        
        if 'error' not in result:
            print(f"Response: {result['response']}")
            print(f"Latency: {result['latency']:.2f}s")
        else:
            print(f"Error: {result['error']}")
        
        # RAG test
        print("\nTest 2: RAG query")
        context_docs = [
            "A deductible is the amount you must pay out-of-pocket before your insurance starts covering costs.",
            "Most health insurance plans have annual deductibles ranging from $500 to $5000."
        ]
        
        result = handler.generate_with_context(
            query="What is a deductible?",
            context_documents=context_docs
        )
        
        if 'error' not in result:
            print(f"Response: {result['response']}")
            print(f"Latency: {result['latency']:.2f}s")
            print(f"Context docs used: {result['num_context_docs']}")
        else:
            print(f"Error: {result['error']}")
    else:
        print("\n⚠ llama3 not available. Install with: ollama pull llama3")


def main():
    """Main execution function"""
    test_model()


if __name__ == "__main__":
    main()
