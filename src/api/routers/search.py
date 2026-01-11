from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json

from src.core.vector_store import vector_store
from src.agents.sdg_classifier import SDGClassifier

router = APIRouter()


@router.get("/")
async def search_documents(
    q: str = Query(..., description="Search query"),
    sdg_goal: Optional[str] = Query(None, description="Filter by SDG goal (1-17)"),
    limit: int = Query(10, ge=1, le=100, description="Number of results")
):
    """Search for documents using RAG"""
    
    try:
        # Build search query
        search_query = q
        if sdg_goal:
            search_query += f" sdg_goal:{sdg_goal}"
        
        # Search vector store
        results = await vector_store.search(search_query, n_results=limit)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "document_id": result["metadata"]["document_id"],
                "filename": result["metadata"]["filename"],
                "content": result["text"],
                "sdg_goals": result["metadata"].get("sdg_goals", []),
                "relevance_score": 1 - result["distance"] if result["distance"] else None,
                "source": result["metadata"].get("source", ""),
                "chunk_info": {
                    "chunk_index": result["metadata"].get("chunk_index", 0),
                    "created_at": result["metadata"].get("created_at", "")
                }
            })
        
        return {
            "query": q,
            "sdg_filter": sdg_goal,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., description="Semantic search query"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Similarity threshold"),
    limit: int = Query(10, ge=1, le=100, description="Number of results")
):
    """Advanced semantic search with similarity threshold"""
    
    try:
        # Search with higher limit to filter by threshold
        results = await vector_store.search(q, n_results=limit * 2)
        
        # Filter by similarity threshold
        filtered_results = []
        for result in results:
            similarity = 1 - result["distance"] if result["distance"] else 0
            if similarity >= threshold:
                filtered_results.append({
                    "document_id": result["metadata"]["document_id"],
                    "filename": result["metadata"]["filename"],
                    "content": result["text"],
                    "sdg_goals": result["metadata"].get("sdg_goals", []),
                    "similarity_score": similarity,
                    "source": result["metadata"].get("source", "")
                })
        
        return {
            "query": q,
            "threshold": threshold,
            "results": filtered_results[:limit],
            "total_results": len(filtered_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search error: {str(e)}")


@router.get("/classify")
async def classify_query(query: str = Query(..., description="Query to classify")):
    """Classify a query by SDG goals using AI"""
    
    try:
        classifier = SDGClassifier()
        classification = await classifier.classify_text(query)
        
        return {
            "query": query,
            "classification": classification,
            "suggested_search": f"{query} sdg_goal:{classification['primary_goal']}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@router.get("/similar/{document_id}")
async def find_similar_documents(
    document_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of similar documents")
):
    """Find documents similar to a specific document"""
    
    try:
        # Get the document content
        results = await vector_store.search(f"document_id:{document_id}", n_results=1)
        
        if not results:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Use the document content to find similar documents
        original_content = results[0]["text"]
        similar_results = await vector_store.search(original_content, n_results=limit + 1)
        
        # Remove the original document from results
        similar_docs = []
        for result in similar_results:
            if result["metadata"]["document_id"] != document_id:
                similar_docs.append({
                    "document_id": result["metadata"]["document_id"],
                    "filename": result["metadata"]["filename"],
                    "content": result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"],
                    "sdg_goals": result["metadata"].get("sdg_goals", []),
                    "similarity_score": 1 - result["distance"] if result["distance"] else None
                })
        
        return {
            "original_document_id": document_id,
            "similar_documents": similar_docs[:limit],
            "total_similar": len(similar_docs)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar documents: {str(e)}")