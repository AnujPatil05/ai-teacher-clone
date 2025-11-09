import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_teaching_style():
    """Extract teaching patterns from transcripts"""
    
    with open("transcripts/combined.json", 'r', encoding='utf-8') as f:
        transcripts = json.load(f)
    
    # Combine all text
    full_text = "\n\n".join([t["text"] for t in transcripts])
    
    analysis_prompt = f"""
Analyze this teacher's (Gate Smashers) teaching style based on these lecture transcripts:

{full_text[:8000]}  # First 8000 chars for analysis

Extract and describe:
1. **Communication Style**: Formal/informal, pace, tone
2. **Explanation Pattern**: How they break down concepts (analogies, examples, step-by-step)
3. **Language Mix**: Hindi/English usage patterns
4. **Signature Phrases**: Common expressions, catchphrases
5. **Teaching Techniques**: Questioning style, recap patterns, emphasis methods
6. **Personality Traits**: Enthusiasm level, humor, encouragement style

Provide a detailed profile that can be used to mimic this teaching style.
"""
    
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    for m in genai.list_models():
        print(m.name)

    response = model.generate_content(analysis_prompt)
    
    style_profile = {
        "analysis": response.text,
        "sample_transcripts": full_text[:3000]
    }
    
    with open("models/teaching_style.json", 'w', encoding='utf-8') as f:
        json.dump(style_profile, f, ensure_ascii=False, indent=2)
    
    print("✓ Teaching style analyzed and saved!")
    

    return style_profile

if __name__ == "__main__":
    analyze_teaching_style()
  



    