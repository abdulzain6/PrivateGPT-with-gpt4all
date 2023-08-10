from database import FileManager, SqliteDatabase
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from utils import replace_specials_with_underscores
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import LLMChain
from prompts import CHAT_PROMPT, TITLE_PROMPT
from langchain.llms import GPT4All
import os


class KnowledgeManager:
    def __init__(
        self,
        filemanager: FileManager,
        openai_api_key: str,
        mode: str = "normal",
        conversation_limit=500,
        docs_limit=3000,
        model_dir="./models",
        data_dir="/data"
    ) -> None:
        self.filemanager = filemanager
        self.openai_api_key = openai_api_key
        self.mode = mode
        self.docs_limit = docs_limit
        self.conversation_limit = conversation_limit
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.switch_mode(mode)

        os.makedirs(os.path.join(data_dir, "datastore"), exist_ok=True)
        os.makedirs(os.path.join(data_dir,"cache"), exist_ok=True)
        os.makedirs(os.path.join(data_dir,"private_datastore"), exist_ok=True)

    def switch_mode(self, mode: str):
        assert mode in {"normal", "private"}
        self.mode = mode
        if mode == "normal":
            self.llm = ChatOpenAI(openai_api_key=self.openai_api_key, temperature=0.3)
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
            self.dir_prefix = os.path.join(self.data_dir, "datastore")
        elif mode == "private":
            local_path = os.path.join(self.model_dir, "ggml-gpt4all-j-v1.3-groovy.bin")
            self.llm = GPT4All(model=local_path, verbose=True)
            self.embeddings = HuggingFaceEmbeddings(cache_folder="cache")
            self.dir_prefix = os.path.join(self.data_dir, "private_datastore")

    def add_file(self, file_path: str) -> str:
        try:
            docs = UnstructuredFileLoader(file_path).load()
            file_path = replace_specials_with_underscores(file_path)
            print("=> Loaded file")
            docs = CharacterTextSplitter(chunk_size=1500).split_documents(docs)
            print("=> Embedding file")
            faiss = FAISS.from_documents(docs, self.embeddings)
            faiss.save_local(self.dir_prefix, file_path)
            self.filemanager.create_file(
                file_name=file_path,
                description="",
                content="<SEPERATOR>".join([doc.page_content for doc in docs]),
                mode=self.mode,
            )
            print("=> Added db")
            return file_path
        except ValueError as e:
            print(e)
            return ""

    def delete_file(self, file_path: str) -> None:
        try:
            os.remove(os.path.join(self.dir_prefix, f"{file_path}.pkl"))
            os.remove(os.path.join(self.dir_prefix, f"{file_path}.faiss"))
        except Exception:
            print("File not found")

        try:
            file_path = replace_specials_with_underscores(file_path)
            self.filemanager.delete_file(file_name=file_path, mode=self.mode)
        except Exception:
            print("Not found in database")

    def make_chain(self):
        return load_qa_with_sources_chain(
            llm=self.llm, prompt=CHAT_PROMPT, verbose=True
        )

    def chat(self, file_name: str, message: str, chat_history: list = None) -> str:
        if chat_history is None:
            chat_history = []

        conversation = self.format_messages(
            chat_history=chat_history, tokens_limit=self.conversation_limit
        )
        combined = (
            self.format_messages(
                chat_history=chat_history,
                tokens_limit=self.conversation_limit,
                human_only=True,
            )
            + "\n"
            + f"Human: {message}"
        )

        file = self.filemanager.read_file(
            self.mode, replace_specials_with_underscores(file_name)
        )
        if not file:
            return "File not found"

        faiss = FAISS.load_local(
            self.dir_prefix, self.embeddings, index_name=file.file_name
        )
        docs = faiss.similarity_search(combined)
        docs = self._reduce_tokens_below_limit(
            RecursiveCharacterTextSplitter(chunk_size=500).split_documents(docs),
            self.docs_limit,
        )

        chain = self.make_chain()
        return chain.run(
            conversation=conversation, question=message, input_documents=docs
        )

    def _reduce_tokens_below_limit(self, docs: list, docs_limit: int):
        num_docs = len(docs)
        tokens = [len(doc.page_content) for doc in docs]
        token_count = sum(tokens[:num_docs])
        while token_count > docs_limit:
            num_docs -= 1
            token_count -= tokens[num_docs]

        return docs[:num_docs]

    def get_title(self, chat_history) -> str:
        conversation = self.format_messages(
            chat_history=chat_history, tokens_limit=4000
        )
        chain = LLMChain(prompt=TITLE_PROMPT, llm=self.llm, verbose=True)
        return chain.run(convo=conversation)

    def format_messages(
        self,
        chat_history: list[tuple[str, str]],
        tokens_limit: int,
        human_only: bool = False,
    ) -> str:
        chat_history = [
            (f"Human: {history[0]}", f"AI: {history[1]}") for history in chat_history
        ]
        tokens_used = 0
        cleaned_msgs = []
        for history in reversed(chat_history):
            if not human_only:
                tokens_used += len(history[0]) + len(history[1])
            else:
                tokens_used += len(history[0])

            if tokens_used > tokens_limit:
                break

            if human_only:
                cleaned_msgs.append(history[0])
            else:
                cleaned_msgs.append((history[0], history[1]))

        if not human_only:
            return "\n\n".join(
                reversed(
                    [clean_msg[0] + "\n\n" + clean_msg[1] for clean_msg in cleaned_msgs]
                )
            )
        else:
            return "\n\n".join(reversed(cleaned_msgs))

