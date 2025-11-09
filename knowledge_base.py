import json
import os
from dotenv import load_dotenv

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
# Optional: Gemini fallback
# from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def create_knowledge_base():
    """Create vector database from transcripts"""

    # Load transcripts
    with open("transcripts/combined.json", 'r', encoding='utf-8') as f:
        transcripts = json.load(f)

    for i, t in enumerate(transcripts):
        if "file" not in t:
            print(f"⚠️ Transcript {i} missing 'file' key")

    # Create documents
    documents = []
    for transcript in transcripts:
        for segment in transcript.get("segments", []):
            doc = Document(
                page_content=segment["text"],
                metadata={
                    "file": transcript.get("file", "unknown"),
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0)
                }
            )
            documents.append(doc)

    print(f"📄 Created {len(documents)} document chunks")

    # Split text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    print(f"🔪 Split into {len(splits)} chunks")

    # Create embeddings (Hugging Face default)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Optional Gemini fallback (commented out)
    # embeddings = GoogleGenerativeAIEmbeddings(
    #     model="models/embedding-001",
    #     google_api_key=os.getenv("GEMINI_API_KEY")
    # )

    # Create vector store
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    vectordb.persist()
    print("✅ Knowledge base created successfully!")

    return vectordb

if __name__ == "__main__":
    create_knowledge_base()