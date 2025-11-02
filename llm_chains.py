from prompt_templates import memory_prompt_template
from langchain.chains import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
# from langchain.llms import CTransformers
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
import chromadb
import yaml
# from create_embeddings import SimpleEmbedding

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def create_llm():
    llm = Ollama(model="llama3")
    return llm



# A function to download the Hugging Face embeddings
def create_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings

# A function to create a chat memory
def create_chat_memory(chat_history):
    return ConversationBufferWindowMemory(memory_key="history", chat_memory=chat_history, k=3)

# A function to create a prompt from a template
def create_prompt_from_template(template):
    return PromptTemplate.from_template(template)

# A function to create an LLM chain
def create_llm_chain(llm, chat_prompt, memory):
    return LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

# A function to load the normal chain
def load_normal_chain(chat_history):
    return chatChain(chat_history)

# A function to load the vector database
def load_vectordb(embeddings):
    persistent_client = chromadb.PersistentClient("chroma_db")

    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name="pdfs",
        embedding_function=embeddings,
    )

    return langchain_chroma

# A function to load the pdf chat chain
def load_pdf_chat_chain(chat_history):
    return pdfChatChain(chat_history)

# A function to add documents to the database
def load_retrieval_chain(llm, memory, vector_db):
    return RetrievalQA.from_llm(llm=llm, memory=memory, retriever=vector_db.as_retriever(kwargs={"k": 3}))

# A class to create a pdf chat chain
class pdfChatChain:

    def __init__(self, chat_history):
        self.memory = create_chat_memory(chat_history)
        self.vector_db = load_vectordb(create_embeddings())
        llm = create_llm()
        #chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = load_retrieval_chain(llm, self.memory, self.vector_db)

    def run(self, user_input):
        print("Pdf chat chain is running...")
        return self.llm_chain.run(query = user_input, history=self.memory.chat_memory.messages ,stop=["Human:"])
    
# A class to create a chat chain

class chatChain:

    def __init__(self, chat_history):
        self.memory = create_chat_memory(chat_history)
        llm = create_llm()
        chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = create_llm_chain(llm, chat_prompt, self.memory)

    def run(self, user_input):
        return self.llm_chain.run(human_input = user_input, history=self.memory.chat_memory.messages ,stop=["Human:"])