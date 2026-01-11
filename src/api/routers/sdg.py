from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json

from src.agents.sdg_classifier import SDGClassifier
from src.core.vector_store import vector_store

router = APIRouter()


@router.get("/goals")
async def get_sdg_goals():
    """Get all SDG goals with descriptions"""
    
    sdg_goals = {
        "1": {"title": "No Poverty", "description": "End poverty in all its forms everywhere"},
        "2": {"title": "Zero Hunger", "description": "End hunger, achieve food security and improved nutrition"},
        "3": {"title": "Good Health and Well-being", "description": "Ensure healthy lives and promote well-being"},
        "4": {"title": "Quality Education", "description": "Ensure inclusive and equitable quality education"},
        "5": {"title": "Gender Equality", "description": "Achieve gender equality and empower all women and girls"},
        "6": {"title": "Clean Water and Sanitation", "description": "Ensure availability and sustainable management of water"},
        "7": {"title": "Affordable and Clean Energy", "description": "Ensure access to affordable, reliable, sustainable energy"},
        "8": {"title": "Decent Work and Economic Growth", "description": "Promote sustained, inclusive and sustainable economic growth"},
        "9": {"title": "Industry, Innovation and Infrastructure", "description": "Build resilient infrastructure, promote inclusive industrialization"},
        "10": {"title": "Reduced Inequalities", "description": "Reduce inequality within and among countries"},
        "11": {"title": "Sustainable Cities and Communities", "description": "Make cities and human settlements inclusive, safe, resilient"},
        "12": {"title": "Responsible Consumption and Production", "description": "Ensure sustainable consumption and production patterns"},
        "13": {"title": "Climate Action", "description": "Take urgent action to combat climate change and its impacts"},
        "14": {"title": "Life Below Water", "description": "Conserve and sustainably use the oceans, seas and marine resources"},
        "15": {"title": "Life on Land", "description": "Protect, restore and promote sustainable use of terrestrial ecosystems"},
        "16": {"title": "Peace, Justice and Strong Institutions", "description": "Promote peaceful and inclusive societies for sustainable development"},
        "17": {"title": "Partnerships for the Goals", "description": "Strengthen the means of implementation and revitalize the global partnership"}
    }
    
    return {"sdg_goals": sdg_goals}


@router.get("/goals/{goal_id}/documents")
async def get_documents_by_sdg_goal(goal_id: str, limit: int = 20):
    """Get documents related to a specific SDG goal"""
    
    if goal_id not in [str(i) for i in range(1, 18)]:
        raise HTTPException(status_code=400, detail="Invalid SDG goal ID. Must be 1-17")
    
    try:
        # Search for documents with this SDG goal
        search_query = f"sdg_goal:{goal_id}"
        results = await vector_store.search(search_query, n_results=limit)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "document_id": result["metadata"]["document_id"],
                "filename": result["metadata"]["filename"],
                "content": result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"],
                "sdg_goals": result["metadata"].get("sdg_goals", []),
                "source": result["metadata"].get("source", ""),
                "relevance_score": 1 - result["distance"] if result["distance"] else None
            })
        
        return {
            "goal_id": goal_id,
            "goal_title": get_sdg_goal_title(goal_id),
            "documents": formatted_results,
            "total_documents": len(formatted_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving SDG documents: {str(e)}")


@router.get("/goals/overview")
async def get_sdg_overview():
    """Get overview of documents across all SDG goals"""
    
    try:
        overview = {}
        
        for goal_id in range(1, 18):
            search_query = f"sdg_goal:{goal_id}"
            results = await vector_store.search(search_query, n_results=100)
            
            overview[str(goal_id)] = {
                "goal_id": goal_id,
                "title": get_sdg_goal_title(str(goal_id)),
                "document_count": len(results),
                "sample_documents": [
                    {
                        "document_id": result["metadata"]["document_id"],
                        "filename": result["metadata"]["filename"],
                        "preview": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
                    }
                    for result in results[:3]  # Show first 3 documents
                ]
            }
        
        return {"sdg_overview": overview}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SDG overview: {str(e)}")


@router.post("/classify/document")
async def classify_document_by_sdg(document_id: str):
    """Classify a document by SDG goals using AI"""
    
    try:
        # Get document content
        results = await vector_store.search(f"document_id:{document_id}", n_results=1)
        
        if not results:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Classify the document
        classifier = SDGClassifier()
        classification = await classifier.classify_text(results[0]["text"])
        
        return {
            "document_id": document_id,
            "classification": classification,
            "confidence": classification.get("confidence", 0),
            "primary_goal": classification.get("primary_goal", ""),
            "secondary_goals": classification.get("secondary_goals", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying document: {str(e)}")


@router.get("/goals/cross-reference")
async def get_sdg_cross_reference():
    """Get cross-reference analysis between SDG goals"""
    
    try:
        cross_reference = {}
        
        for goal_id in range(1, 18):
            search_query = f"sdg_goal:{goal_id}"
            results = await vector_store.search(search_query, n_results=50)
            
            # Find related goals
            related_goals = {}
            for result in results:
                doc_sdg_goals = result["metadata"].get("sdg_goals", [])
                for related_goal in doc_sdg_goals:
                    if related_goal != str(goal_id):
                        related_goals[related_goal] = related_goals.get(related_goal, 0) + 1
            
            # Sort by frequency
            sorted_related = sorted(related_goals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            cross_reference[str(goal_id)] = {
                "goal_id": goal_id,
                "title": get_sdg_goal_title(str(goal_id)),
                "related_goals": [
                    {
                        "goal_id": goal,
                        "title": get_sdg_goal_title(goal),
                        "co_occurrence": count
                    }
                    for goal, count in sorted_related
                ]
            }
        
        return {"cross_reference": cross_reference}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cross-reference: {str(e)}")


def get_sdg_goal_title(goal_id: str) -> str:
    """Get SDG goal title by ID"""
    goals = {
        "1": "No Poverty",
        "2": "Zero Hunger",
        "3": "Good Health and Well-being",
        "4": "Quality Education",
        "5": "Gender Equality",
        "6": "Clean Water and Sanitation",
        "7": "Affordable and Clean Energy",
        "8": "Decent Work and Economic Growth",
        "9": "Industry, Innovation and Infrastructure",
        "10": "Reduced Inequalities",
        "11": "Sustainable Cities and Communities",
        "12": "Responsible Consumption and Production",
        "13": "Climate Action",
        "14": "Life Below Water",
        "15": "Life on Land",
        "16": "Peace, Justice and Strong Institutions",
        "17": "Partnerships for the Goals"
    }
    return goals.get(goal_id, "Unknown Goal")