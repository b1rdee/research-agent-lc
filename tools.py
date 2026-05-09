#from langchain_community.tools import SerperAPIWrapper
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
import os

# Initialize the SerperAPIWrapper with your API key
search = GoogleSerperAPIWrapper(serper_api_key=os.getenv("SERPER_API_KEY"),k=20)


# Wrap the run method as a tool
@tool

def web_search(query:str) -> str :
    """Search the web using Serper API for up-to-date information."""
    return search.run(query)
    

