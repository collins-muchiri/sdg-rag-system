import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import asyncio

from config.settings import settings


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_db_path)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.collection = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    async def init_collection(self):
        """Initialize Chroma collection"""
        try:
            self.collection = self.client.get_or_create_collection(
                name="sdg_documents",
                metadata={"description": "SDG documents collection"}
            )
        except Exception as e:
            print(f"Error initializing collection: {e}")
            raise
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to vector store"""
        if not self.collection:
            await self.init_collection()
        
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            # Split text into chunks
            chunks = self.text_splitter.split_text(doc["text"])
            
            for i, chunk in enumerate(chunks):
                doc_id = f"{doc['id']}_chunk_{i}"
                ids.append(doc_id)
                texts.append(chunk)
                metadatas.append({
                    "document_id": doc["id"],
                    "filename": doc.get("filename", ""),
                    "sdg_goals": doc.get("sdg_goals", []),
                    "chunk_index": i,
                    "source": doc.get("source", ""),
                    "created_at": doc.get("created_at", ""),
                })
        
        # Add to Chroma
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.collection:
            await self.init_collection()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })
        
        return formatted_results
    
    async def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        if not self.collection:
            await self.init_collection()
        
        # Get all chunk IDs for this document
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if results["ids"]:
            self.collection.delete(ids=results["ids"])


# Global vector store instance
vector_store = VectorStore()


async def init_vector_store():
    """Initialize vector store"""
    await vector_store.init_collection()
    print("Vector store initialized successfully")