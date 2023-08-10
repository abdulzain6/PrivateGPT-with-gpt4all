from ai import FileManager, SqliteDatabase, KnowledgeManager
from database import ChatManager
import os


MODEL_DIR = "./models"
DATA_PATH = os.environ["DATA_PATH"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DATABASE_PATH = os.path.join(DATA_PATH, "database.db")


file_manager = FileManager(SqliteDatabase(DATABASE_PATH))
knowledge_manager = KnowledgeManager(file_manager, OPENAI_API_KEY, model_dir=MODEL_DIR, data_dir=DATA_PATH)
chat_manager = ChatManager(SqliteDatabase(DATABASE_PATH))