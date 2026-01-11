from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import shutil

from config.settings import settings
from src.core.database import get_db
from src.processors.document_processor import DocumentProcessor
from src.core.vector_store import vector_store

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    
    # Validate file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.supported_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(settings.supported_formats)}"
        )
    
    # Generate unique filename
    document_id = str(uuid.uuid4())
    filename = f"{document_id}.{file_extension}"
    file_path = os.path.join(settings.upload_dir, filename)
    
    # Save file
    os.makedirs(settings.upload_dir, exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process document
        processor = DocumentProcessor()
        processed_doc = await processor.process_document(file_path, document_id, file.filename)
        
        # Add to vector store
        await vector_store.add_documents([processed_doc])
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "processed",
            "sdg_goals": processed_doc.get("sdg_goals", []),
            "chunks_count": len(processed_doc.get("text", "").split()) // 200  # Approximate
        }
    
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get document information"""
    
    try:
        # Search for document in vector store
        results = await vector_store.search(f"document_id:{document_id}", n_results=1)
        
        if not results:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": document_id,
            "metadata": results[0]["metadata"],
            "preview": results[0]["text"][:500] + "..." if len(results[0]["text"]) > 500 else results[0]["text"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    
    try:
        # Remove from vector store
        await vector_store.delete_document(document_id)
        
        # Remove file from storage
        for ext in settings.supported_formats:
            file_path = os.path.join(settings.upload_dir, f"{document_id}.{ext}")
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return {"message": "Document deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.get("/")
async def list_documents():
    """List all documents"""
    
    try:
        # This would require a metadata database in production
        # For now, return a placeholder
        return {
            "documents": [],
            "message": "Document listing requires metadata database implementation"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")