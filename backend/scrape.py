import os
import json
import requests
from typing import List, Optional
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv


load_dotenv()
# ==========================================
# 1. CONFIGURATION
# ==========================================

# ==========================================
# 2. DEFINE YOUR DATABASE SCHEMA
# ==========================================
class Scholarship(BaseModel):
    name: str = Field(..., description="The official name of the scholarship")
    description: str = Field(..., description="A 1-sentence summary of who it is for")
    link: str = Field(..., description="The direct URL to the application")
    eligibility: List[str] = Field(..., description="List of keywords like 'high school senior', 'low-income', 'STEM'")
    application_open: Optional[str] = Field(None, description="Date in YYYY-MM-DD format. If unknown, use null.")
    deadline: Optional[str] = Field(None, description="Date in YYYY-MM-DD format. If unknown, use null.")
    amount: Optional[str] = Field(None, description="The dollar amount or 'Full Tuition'")

class ScholarshipList(BaseModel):
    scholarships: List[Scholarship]

# ==========================================
# 3. THE SCRAPING AGENT
# ==========================================
def scrape_scholarships(target_url: str):
    print(f"🕵️  Scraping: {target_url}...")
    
    # STEP A: Fetch clean Markdown using Jina.ai (Free, no key required)
    # This turns a messy website into clean text for the AI.
    jina_url = f"https://r.jina.ai/{target_url}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        markdown_text = response.text
        
        if not markdown_text or len(markdown_text) < 100:
            return {"error": "Failed to retrieve meaningful content from URL", "scholarships": []}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching URL: {str(e)}", "scholarships": []}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "scholarships": []}

    print(f"✅  Website content retrieved ({len(markdown_text)} chars). Analyzing with AI...")

    # STEP B: Send to Groq (Llama 3) for extraction
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return {"error": "GROQ_API_KEY environment variable not set", "scholarships": []}
            
        client = Groq(api_key=api_key)
        
        # Get JSON schema
        schema = ScholarshipList.model_json_schema()
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated to current model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Data Engineering Agent. Your goal is to extract scholarship information "
                        "from website text into strict JSON format.\n"
                        "- Convert all relative dates (e.g., 'next Friday') to YYYY-MM-DD format assuming the current year is 2025/2026.\n"
                        "- If the link is missing, use the original source URL.\n"
                        "- Only extract valid scholarships. Ignore ads or navigation links.\n"
                        "- Return a JSON object with a 'scholarships' array containing all extracted scholarships.\n"
                        f"Required JSON structure: {json.dumps(schema, indent=2)}"
                    )
                },
                {
                    "role": "user",
                    "content": f"Extract scholarships from this text:\n\n{markdown_text[:15000]}"  # Truncate to avoid limits
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=4000
        )

        # STEP C: Parse and Return
        try:
            result = json.loads(completion.choices[0].message.content)
            
            # Validate the result matches our schema
            if "scholarships" not in result:
                return {"error": "AI response missing 'scholarships' key", "scholarships": []}
            
            # Ensure it's a list
            if not isinstance(result["scholarships"], list):
                return {"error": "AI response 'scholarships' is not a list", "scholarships": []}
            
            return result
            
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON from AI response: {str(e)}", "scholarships": []}
        except Exception as e:
            return {"error": f"Error processing AI response: {str(e)}", "scholarships": []}
            
    except Exception as e:
        return {"error": f"Groq API error: {str(e)}", "scholarships": []}

# ==========================================
# 4. RUN IT
# ==========================================
if __name__ == "__main__":
    test_url = "https://www.unr.edu/financial-aid/scholarships/external-scholarships"
    
    data = scrape_scholarships(test_url)
    
    # Print the result nicely
    print(json.dumps(data, indent=2))
    
    # Save to a new file for review
    if "scholarships" in data and not data.get("error"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"scraped_scholarships_{timestamp}.json"
        
        with open(output_path, "w") as f:
            json.dump(data["scholarships"], f, indent=2)
        
        print(f"\n✅ Saved {len(data['scholarships'])} scholarships to {output_path}")
        print(f"   Review and manually merge into frontend/public/scholarships.json")
    else:
        print(f"\n❌ Error: {data.get('error', 'Unknown error')}")