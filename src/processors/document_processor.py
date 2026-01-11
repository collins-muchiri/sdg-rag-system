from unstructured.partition.auto import partition
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Dict, Any, List
import os
import uuid
from datetime import datetime

from src.agents.sdg_classifier import SDGClassifier


class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.sdg_classifier = SDGClassifier()
    
    async def process_document(self, file_path: str, document_id: str, filename: str) -> Dict[str, Any]:
        """Process a document and extract text, metadata, and SDG classification"""
        
        try:
            # Extract text using unstructured
            elements = partition(filename=file_path)
            
            # Combine text from all elements
            full_text = "\n".join([str(element) for element in elements])
            
            if not full_text.strip():
                raise ValueError("No text could be extracted from the document")
            
            # Classify document by SDG goals
            sdg_classification = await self.sdg_classifier.classify_text(full_text)
            
            # Extract metadata
            metadata = self._extract_metadata(elements, filename, document_id)
            
            # Create processed document
            processed_doc = {
                "id": document_id,
                "text": full_text,
                "filename": filename,
                "file_type": self._get_file_type(filename),
                "sdg_goals": sdg_classification.get("goals", []),
                "primary_sdg_goal": sdg_classification.get("primary_goal", ""),
                "confidence": sdg_classification.get("confidence", 0),
                "metadata": metadata,
                "source": "file_upload",
                "created_at": datetime.now().isoformat(),
                "processed_at": datetime.now().isoformat(),
                "element_count": len(elements),
                "text_length": len(full_text)
            }
            
            return processed_doc
        
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    def _extract_metadata(self, elements: List, filename: str, document_id: str) -> Dict[str, Any]:
        """Extract metadata from document elements"""
        
        metadata = {
            "document_id": document_id,
            "filename": filename,
            "file_size": os.path.getsize(filename) if os.path.exists(filename) else 0,
            "element_types": [],
            "language": "en",  # Default, could be detected
            "processing_timestamp": datetime.now().isoformat()
        }
        
        # Count element types
        element_types = {}
        for element in elements:
            element_type = str(type(element).__name__)
            element_types[element_type] = element_types.get(element_type, 0) + 1
        
        metadata["element_types"] = element_types
        
        # Extract title if available
        titles = [str(element) for element in elements if "title" in str(type(element)).lower()]
        if titles:
            metadata["title"] = titles[0][:200]  # First title, truncated
        
        return metadata
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename"""
        extension = filename.split('.')[-1].lower()
        type_mapping = {
            "pdf": "pdf",
            "docx": "word",
            "doc": "word",
            "txt": "text",
            "md": "markdown",
            "pptx": "powerpoint",
            "ppt": "powerpoint"
        }
        return type_mapping.get(extension, "unknown")
    
    async def batch_process_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple documents in batch"""
        
        results = []
        
        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                document_id = str(uuid.uuid4())
                
                processed_doc = await self.process_document(file_path, document_id, filename)
                results.append(processed_doc)
            
            except Exception as e:
                # Log error but continue processing other documents
                error_doc = {
                    "filename": os.path.basename(file_path),
                    "error": str(e),
                    "status": "failed"
                }
                results.append(error_doc)
        
        return results
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text (simple implementation)"""
        
        # This is a simplified implementation
        # In production, you'd use NLP libraries like spaCy or NLTK
        words = text.lower().split()
        
        # Filter out common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have",
            "has", "had", "do", "does", "did", "will", "would", "could", "should"
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count word frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most common words
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in common_words[:max_phrases]]