# Health Insurance AI Assistant - Quick Start Guide

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Ollama

**Windows:**
Download and install from [ollama.ai/download](https://ollama.ai/download)

### Step 2: Start Ollama Service

```powershell
# Open a new terminal and run:
ollama serve
```

Keep this terminal open.

### Step 3: Download Models

```powershell
# In a new terminal:
ollama pull llama3
ollama pull mistral
ollama pull phi3
```

### Step 4: Setup Python Environment

```powershell
# Navigate to project
cd C:\Capstone-Suha-Demo

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Initialize Data

```powershell
# Process documents
python src\data_processing.py

# Initialize vector store
python src\vector_store.py
```

### Step 6: Run the Demo!

**Option A: Web Interface (Recommended)**
```powershell
streamlit run src\app.py
```
Opens at http://localhost:8501

**Option B: Command Line**
```powershell
# Interactive mode
python src\rag_pipeline.py

# Demo mode
python src\rag_pipeline.py demo
```

---

## 🎯 Try These Questions

1. "What is a deductible?"
2. "How do I file a claim for an emergency room visit?"
3. "What mental health services are covered?"
4. "What is the difference between HMO and PPO?"
5. "Are preventive care services free?"

---

## 🚨 Troubleshooting

### "Error: Connection refused"
→ Make sure Ollama is running: `ollama serve`

### "Model 'llama3' not found"
→ Download the model: `ollama pull llama3`

### "No module named 'langchain'"
→ Install dependencies: `pip install -r requirements.txt`

### "No documents in vector store"
→ Initialize data:
```powershell
python src\data_processing.py
python src\vector_store.py
```

---

## 📊 Project Structure

```
Capstone-Suha-Demo/
├── src/               # Source code
│   ├── app.py        # Streamlit web app
│   ├── rag_pipeline.py
│   ├── model_handler.py
│   ├── vector_store.py
│   └── data_processing.py
├── data/             # Data and vectors
├── docs/             # Documentation
├── tests/            # Unit tests
└── notebooks/        # Jupyter notebooks
```

---

## 📖 Full Documentation

- [README.md](README.md) - Complete project overview
- [CAPSTONE_REPORT.md](docs/CAPSTONE_REPORT.md) - Full capstone report
- [MODEL_COMPARISON.md](docs/MODEL_COMPARISON.md) - Model evaluation details
- [DEMO_GUIDE.md](docs/DEMO_GUIDE.md) - Demo presentation guide

---

## 🎓 Capstone Evaluation

This project demonstrates:

✅ **Functional Completeness** - Complete RAG system  
✅ **RAG Design** - ChromaDB + semantic search  
✅ **Prompt Engineering** - Multiple strategies tested  
✅ **Code Quality** - Well-structured Python code  
✅ **AI-Assisted Development** - Built with GitHub Copilot  
✅ **Testing** - Unit tests included  
✅ **Engineering Judgment** - Model comparison and selection  
✅ **Documentation** - Comprehensive docs and reports  

**Total Score Target:** 150/150 points

---

## 🚀 Next Steps

1. Run the demo
2. Review the documentation
3. Explore the Jupyter notebooks
4. Run tests: `pytest tests/ -v`
5. Customize for your use case

---

**Questions?** Check the [DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for detailed instructions.

**Good luck with your capstone! 🎉**
