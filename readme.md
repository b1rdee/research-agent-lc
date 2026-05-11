# 🔍 LangChain Research Agent – Gemini & Ollama

**LangChain Research Agent** is a Streamlit‑based web application that researches any topic you ask. It uses a **LangGraph** workflow (researcher → writer → critic) to search the web via Serper API and produce a detailed, well‑structured summary (≥500 words). The agent can run on two different LLM backends:

- **Google Gemini** (cloud, via OpenAI‑compatible endpoint) – fast, high‑quality.
- **Ollama** (self‑hosted, with e.g. Qwen2.5 3B) – private, no API costs.

👉 **Live demo (Gemini):** [https://your-gemini-service.up.railway.app](https://your-gemini-service.up.railway.app)  
👉 **Live demo (Ollama):** [https://your-ollama-service.up.railway.app](https://your-ollama-service.up.railway.app)  
*(Replace with your actual Railway URLs)*

---

## ✨ Features

- Natural language input – just type a topic  
- Web search via **Serper API** (Google Search)  
- **LangGraph** workflow:  
  - `researcher` – searches the web  
  - `writer` – writes a detailed summary  
  - `critic` – checks length and requests improvements (loop until ≥500 words)  
- **Backend switching** – choose Gemini or Ollama via a single environment variable  
- Dockerised – runs anywhere  
- Deployed on **Railway** (Git‑based CI/CD)

---

## 🛠️ Tech Stack

| Layer              | Technology                                                                 |
|--------------------|----------------------------------------------------------------------------|
| Frontend           | [Streamlit](https://streamlit.io)                                          |
| Agent Workflow     | [LangGraph](https://www.langchain.com/langgraph) + [LangChain](https://www.langchain.com) |
| LLM (cloud)        | [Google Gemini](https://ai.google.dev/gemini-api) via OpenAI‑compatible endpoint |
| LLM (self‑hosted)  | [Ollama](https://ollama.com) with [Qwen2.5 3B](https://ollama.com/library/qwen2.5:3b) |
| Web Search         | [Serper API](https://serper.dev)                                           |
| Container          | Docker                                                                     |
| Deployment         | [Railway](https://railway.app)                                             |

---

## 🚀 Getting Started (Local Development)

**Prerequisites**

- Python 3.9+
- Docker (optional, but recommended)
- API keys: [Gemini](https://aistudio.google.com/app/apikey) (if using Gemini) + [Serper](https://serper.dev)
- For Ollama backend: [Install Ollama](https://ollama.com/download) and pull a model (e.g. `ollama pull qwen2.5:3b`)

1. **Clone the repository**

   ```
   git clone https://github.com/YOUR_USERNAME/langchain-research-agent.git
   cd langchain-research-agent
   ```

2.  **Set up environment variables**

      Create a `.env` file in the project root.

      **Option 1: Use Gemini (default backend)**
      ```
      GEMINI_API_KEY=your_gemini_key_here
      SERPER_API_KEY=your_serper_key_here
      # LLM_BACKEND defaults to 'gemini', so no need to set it
      ```      

      **Option 2: Use Ollama(self-hosted)**
      
      ```
      LLM_BACKEND=ollama
      OLLAMA_BASE_URL=http://localhost:11434
      OLLAMA_MODEL=qwen2.5:3b
      SERPER_API_KEY=your_serper_key_here

      ⚠️ Never commit .env – it's already ignored via .gitignore.
      ```

3. Run without Docker

   ```
   pip install -r requirements.txt
   streamlit run app.py
   http://localhost:8501

4. Run with Docker (test the container)
      ```
      docker build -t langchain-research-agent .
      docker run -p 7860:7860 langchain-research-agent

## Switching Between Gemini and Ollama Backends

The agent reads the `LLM_BACKEND` environment variable to decide which LLM to use. The same codebase works for both.

| Backend          | Environment variables                                                                 |
|------------------|----------------------------------------------------------------------------------------|
| **Gemini** (default) | `LLM_BACKEND=gemini` (or not set) + `GEMINI_API_KEY`                                 |
| **Ollama** (local)   | `LLM_BACKEND=ollama` + `OLLAMA_BASE_URL` (default `http://localhost:11434`) + `OLLAMA_MODEL` |
   
                       
## On Railway

- **For the Gemini service:** add `LLM_BACKEND=gemini` (or omit) and `GEMINI_API_KEY`.

- **For the Ollama service:** add `LLM_BACKEND=ollama` and `OLLAMA_BASE_URL=http://ollama.railway.internal:11434` (the internal hostname of your Ollama service). Also set `OLLAMA_MODEL` if different from default.

- **All other settings** (search tool, graph nodes) remain identical.

## 📦  Deployment on Railway (Git‑based)

1. Push your code to a GitHub repository.
2. On [Railway.app](https://railway.app), create a new project → **Deploy from GitHub repo**.
3. Select your repository. Railway automatically detects the `Dockerfile`.
4. Add environment variables:
   - `SERPER_API_KEY`
   - and either:
     - `GEMINI_API_KEY`  
       or
     - `LLM_BACKEND=ollama` + `OLLAMA_BASE_URL`
5. Railway assigns a public URL. Every `git push` triggers an automatic redeploy.

## Running Ollama on Railway

To run Ollama on Railway, you need a **separate Ollama service** (with a persistent volume of ≥5 GB). The agent service can then connect to it using the internal hostname:
http://ollama.railway.internal:11434

## 🧠 How It Works (LangGraph Flow)

The agent uses a **stateful graph** (LangGraph) with four nodes and a conditional loop:

- **Researcher node** – calls `web_search` (Serper) and appends results to `research_notes`.
- **Writer node** – generates an initial draft (or improves an existing one if feedback is present).
- **Critic node** – checks the draft length. If below threshold (e.g., <500 words), it sets `needs_improvement = True` and provides feedback.
- **Conditional edge** – if `needs_improvement` is `True`, the graph loops back to the writer node; otherwise it ends.

### State Dictionary

The state tracks the following fields:

```
{
    "topic": str,                # user query, never changes
    "research_notes": list,      # accumulates search results (with operator.add reducer)
    "draft": str,                # current version of the summary
    "feedback": str,             # critic’s suggestions for improvement
    "needs_improvement": bool,   # loop control flag
    "final_answer": str          # final approved summary (returned to the user)
}
```

## 📁 Project Structure

```text
langchain-research-agent/
├── app.py               # Streamlit frontend
├── graph.py             # LangGraph workflow (researcher, writer, critic)
├── chat_models.py       # LLM factory (Gemini or Ollama)
├── tools.py             # Serper search tool
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
├── .env                 # API keys (not committed)
├── .gitignore           # Ignores .env, __pycache__, etc.
└── README.md            # This file
```

## 🙏 Acknowledgements

- **LangChain & LangGraph** – graph‑based agent framework
- **Google Gemini API** – cloud LLM
- **Ollama** – local LLM runner
- **Qwen2.5** – open‑source model
- **Serper API** – Google Search API
- **Railway** – cloud deployment platform