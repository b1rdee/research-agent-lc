
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

# Determine which LLM to use based on environment variable
api = load_dotenv()
#print(os.getenv("GEMINI_API_KEY"),"Gemini API Key")
#print(os.getenv("SERPER_API_KEY"),"Serper API Key")
#print(os.getenv("LLM_BACKEND"),"OLLAMA API Key")


llm_model = os.getenv("LLM_BACKEND","gemini")
print("llm backend : ",llm_model)

if llm_model == "ollama":
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    llm = ChatOllama(model=model_name, base_url=ollama_base_url, temperature=0.7)
else:
    #defaults to Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview",
        temperature="0.7",
        google_api_key=os.getenv("GEMINI_API_KEY")
        
        )
