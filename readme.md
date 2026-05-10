## LangChain Research Agent with Critic Loop

Multi-agent research system using LangChain, LangGraph, Streamlit.
Performs web search (Serper API), generates >=500 word summary,
and uses a critic loop for self-improvement.
Supports Gemini (cloud) and Ollama (self-hosted).

**Features:**
- Web search (20 results via Serper API)
- LangGraph workflow: researcher -> writer -> critic loop
- Length-based critic (expands drafts under ~500 words)
- Self-improvement: writer incorporates feedback
- Dual backend (Gemini/Ollama via one environment variable)
- Ready for Railway (Docker, persistent volume for Ollama)

**Critic Loop Diagram:**

Start -> Researcher -> Writer -> Critic -> Length >=500 words?
If No: generate feedback -> loop back to Writer
If Yes: End -> return final answer

Tech Stack:
- LangChain + LangGraph
- Streamlit (UI)
- Serper API (search)
- Gemini API / Ollama (LLMs)
- Docker + Railway

Project Structure:
langchain-research-agent/
  app.py
  graph.py
  chat_models.py
  tools.py
  requirements.txt
  Dockerfile
  .env.example
  README.md

Local Setup:

1. Clone the repository:
   git clone https://github.com/yourusername/langchain-research-agent.git
   cd langchain-research-agent

2. Create virtual environment:
   python -m venv venv
   source venv/bin/activate (Linux/Mac) or .\venv\Scripts\activate (Windows)

3. Install dependencies:
   pip install -r requirements.txt

4. Copy environment file:
   cp .env.example .env

5. Edit .env with your keys (see below)

6. Run the app:
   streamlit run app.py

Environment Variables (.env):

LLM_BACKEND=gemini (or ollama)
GEMINI_API_KEY=your_google_key
SERPER_API_KEY=your_serper_key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

Docker (Local):

docker build -t langchain-research-agent .
docker run -p 7860:7860 --env-file .env langchain-research-agent

Deploy on Railway:

Option A: Deploy from GitHub
- Push code to GitHub
- On Railway: New Project -> Deploy from GitHub repo
- Add environment variables

Option B: Deploy from Docker image
- docker build -t yourdockerhub/langchain-research-agent .
- docker push yourdockerhub/langchain-research-agent
- On Railway: New Project -> Deploy from Docker Image

Required environment variables on Railway:
- LLM_BACKEND (gemini or ollama)
- GEMINI_API_KEY (if using Gemini)
- SERPER_API_KEY
- OLLAMA_BASE_URL (if using Ollama, e.g., http://ollama.railway.internal:11434)
- OLLAMA_MODEL (e.g., qwen2.5:3b)

For Ollama on Railway:
- Create a separate Ollama service with persistent volume (5GB hobby limit)
- Set OLLAMA_BASE_URL in the research agent service to point to the Ollama service

Switching Backends:
Simply change LLM_BACKEND environment variable to 'gemini' or 'ollama'. No code changes needed.

Example:
User input: "Latest advances in quantum computing 2025"
Output: A well-structured research summary of 500+ words with recent breakthroughs,
key players, challenges, and future outlook.

If first draft is too short, critic sends feedback like:
"The draft is too short (about 320 words). Please expand with more details on..."
Writer then improves the draft in the next iteration.

Logging & Debugging:
- Logs go to stdout (print statements and Python logging)
- On Railway: use 'railway logs' (CLI) or Dashboard -> Observability -> Logs

Future Improvements (Roadmap):
- Integrate existing RAG project as a new node
- Add LLM-based critic (quality evaluation beyond length)
- Support more search APIs (Tavily, Bing)
- Streaming RAG with real-time data ingestion
- Add scikit-learn classifier as a tool for predictions

License: MIT

Acknowledgements:
LangChain, LangGraph, Serper.dev, Ollama, Railway