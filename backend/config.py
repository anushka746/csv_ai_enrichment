import os 
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


client = Groq(api_key=GROQ_API_KEY)