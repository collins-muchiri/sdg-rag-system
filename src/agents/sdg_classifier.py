from openai import OpenAI
from typing import Dict, List, Any
import json

from config.settings import settings


class SDGClassifier:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.sdg_goals = {
            "1": "No Poverty - End poverty in all its forms everywhere",
            "2": "Zero Hunger - End hunger, achieve food security and improved nutrition",
            "3": "Good Health and Well-being - Ensure healthy lives and promote well-being",
            "4": "Quality Education - Ensure inclusive and equitable quality education",
            "5": "Gender Equality - Achieve gender equality and empower all women and girls",
            "6": "Clean Water and Sanitation - Ensure availability and sustainable management of water",
            "7": "Affordable and Clean Energy - Ensure access to affordable, reliable, sustainable energy",
            "8": "Decent Work and Economic Growth - Promote sustained, inclusive and sustainable economic growth",
            "9": "Industry, Innovation and Infrastructure - Build resilient infrastructure, promote inclusive industrialization",
            "10": "Reduced Inequalities - Reduce inequality within and among countries",
            "11": "Sustainable Cities and Communities - Make cities and human settlements inclusive, safe, resilient",
            "12": "Responsible Consumption and Production - Ensure sustainable consumption and production patterns",
            "13": "Climate Action - Take urgent action to combat climate change and its impacts",
            "14": "Life Below Water - Conserve and sustainably use the oceans, seas and marine resources",
            "15": "Life on Land - Protect, restore and promote sustainable use of terrestrial ecosystems",
            "16": "Peace, Justice and Strong Institutions - Promote peaceful and inclusive societies for sustainable development",
            "17": "Partnerships for the Goals - Strengthen the means of implementation and revitalize the global partnership"
        }
    
    async def classify_text(self, text: str) -> Dict[str, Any]:
        """Classify text by SDG goals using AI"""
        
        try:
            # Prepare the prompt
            prompt = self._create_classification_prompt(text)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=settings.default_model,
                messages=[
                    {"role": "system", "content": "You are an expert in Sustainable Development Goals (SDGs) and can accurately classify text content by relevant SDG goals."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse the response
            classification_text = response.choices[0].message.content
            classification = self._parse_classification_response(classification_text)
            
            return classification
        
        except Exception as e:
            # Fallback to simple keyword-based classification
            return self._fallback_classification(text)
    
    def _create_classification_prompt(self, text: str) -> str:
        """Create classification prompt"""
        
        sdg_list = "\n".join([f"{goal}: {description}" for goal, description in self.sdg_goals.items()])
        
        prompt = f"""
Please analyze the following text and classify it by the most relevant Sustainable Development Goals (SDGs).

SDG Goals:
{sdg_list}

Text to analyze:
{text[:2000]}  # Limit text length for API

Please provide your response in the following JSON format:
{{
    "primary_goal": "Most relevant SDG goal number (1-17)",
    "secondary_goals": ["List of other relevant SDG goal numbers"],
    "confidence": 0.85,
    "reasoning": "Brief explanation of why these goals were selected",
    "key_topics": ["List of main topics identified in the text"]
}}

Focus on identifying the core themes and their relationship to specific SDG goals.
"""
        
        return prompt
    
    def _parse_classification_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the classification response from AI"""
        
        try:
            # Try to extract JSON from response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                classification = json.loads(json_str)
                
                # Validate and normalize
                if "primary_goal" not in classification:
                    classification["primary_goal"] = ""
                
                if "secondary_goals" not in classification:
                    classification["secondary_goals"] = []
                
                if "confidence" not in classification:
                    classification["confidence"] = 0.5
                
                # Convert goals to strings
                classification["goals"] = [classification["primary_goal"]] + classification["secondary_goals"]
                
                return classification
            
            else:
                # Fallback if JSON parsing fails
                return self._create_fallback_classification(response_text)
        
        except Exception:
            return self._create_fallback_classification(response_text)
    
    def _fallback_classification(self, text: str) -> Dict[str, Any]:
        """Fallback classification using keyword matching"""
        
        # Simple keyword-based classification
        sdg_keywords = {
            "1": ["poverty", "poor", "income", "economic", "living standards", "financial"],
            "2": ["hunger", "food", "nutrition", "agriculture", "famine", "malnutrition"],
            "3": ["health", "medical", "disease", "healthcare", "wellness", "medicine"],
            "4": ["education", "learning", "school", "literacy", "knowledge", "training"],
            "5": ["gender", "women", "equality", "female", "empowerment", "discrimination"],
            "6": ["water", "sanitation", "hygiene", "clean water", "toilets", "waste"],
            "7": ["energy", "electricity", "power", "renewable", "solar", "wind"],
            "8": ["employment", "jobs", "work", "labor", "economic growth", "business"],
            "9": ["infrastructure", "industry", "innovation", "technology", "construction"],
            "10": ["inequality", "equality", "social", "discrimination", "fairness"],
            "11": ["cities", "urban", "housing", "transportation", "community", "sustainable cities"],
            "12": ["consumption", "production", "waste", "recycling", "sustainable", "resources"],
            "13": ["climate", "environment", "global warming", "carbon", "emissions", "sustainability"],
            "14": ["oceans", "marine", "sea", "water", "fish", "marine life"],
            "15": ["land", "forests", "biodiversity", "ecosystems", "conservation", "wildlife"],
            "16": ["peace", "justice", "security", "institutions", "governance", "rights"],
            "17": ["partnerships", "cooperation", "collaboration", "global", "international"]
        }
        
        text_lower = text.lower()
        goal_scores = {}
        
        # Score each goal based on keyword matches
        for goal, keywords in sdg_keywords.items():
            score = 0
            for keyword in keywords:
                score += text_lower.count(keyword)
            goal_scores[goal] = score
        
        # Sort by score
        sorted_goals = sorted(goal_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get top goals
        primary_goal = sorted_goals[0][0] if sorted_goals[0][1] > 0 else ""
        secondary_goals = [goal for goal, score in sorted_goals[1:4] if score > 0]
        
        return {
            "primary_goal": primary_goal,
            "secondary_goals": secondary_goals,
            "goals": [primary_goal] + secondary_goals,
            "confidence": 0.3,  # Low confidence for fallback
            "reasoning": "Keyword-based classification (fallback method)",
            "key_topics": []
        }
    
    def _create_fallback_classification(self, response_text: str) -> Dict[str, Any]:
        """Create fallback classification from unstructured response"""
        
        # Extract goal numbers from response
        goals_found = []
        for goal_num in range(1, 18):
            if f"SDG {goal_num}" in response_text or f"goal {goal_num}" in response_text:
                goals_found.append(str(goal_num))
        
        return {
            "primary_goal": goals_found[0] if goals_found else "",
            "secondary_goals": goals_found[1:3] if len(goals_found) > 1 else [],
            "goals": goals_found,
            "confidence": 0.4,
            "reasoning": "Extracted from AI response (fallback parsing)",
            "key_topics": []
        }