import google.generativeai as genai
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
import json
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class TeacherClone:
    def __init__(self):
        # Load teaching style
        with open("models/teaching_style.json", 'r', encoding='utf-8') as f:
            self.style = json.load(f)
        
        # Load vector DB
        embeddings = HuggingFaceEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectordb = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        
        # Initialize Gemini
        self.model = genai.GenerativeModel('models/gemini-2.5-pro')
   
    def get_response(self, question, use_rag=True):
        """Generate response in teacher's style"""
        
        # Retrieve relevant context
        context = ""
        if use_rag:
            docs = self.vectordb.similarity_search(question, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create prompt
        system_prompt = f"""You are an AI clone of Gate Smashers teacher. 

TEACHING STYLE PROFILE:
{self.style['analysis']}

SAMPLE TEACHING EXAMPLES:
{self.style['sample_transcripts'][:1500]}

YOUR PERSONALITY:
- Use a mix of Hindi and English naturally (Hinglish)
- Break down complex concepts into simple steps
- Use real-world analogies and examples
- Be encouraging and enthusiastic
- Use phrases like "dekho", "samjhe?", "simple hai"
- Maintain the energetic, friendly teaching style

CONTEXT FROM LECTURES:
{context if context else "No specific lecture context available"}

INSTRUCTIONS:
1. If the question is about topics covered in lectures, use the context
2. If the question is outside lecture scope (like OS, Polymorphism), still answer in the SAME teaching style
3. Always maintain Gate Smashers' personality and teaching approach
4. Keep responses educational, clear, and engaging
5. Use Hindi-English mix naturally

Question: {question}

Answer as Gate Smashers would teach this:"""

        # Generate response
        response = self.model.generate_content(system_prompt)
        return response.text

# Test
if __name__ == "__main__":
    clone = TeacherClone()
    
    # Test questions
    questions = [
        "DBMS mein normalization kya hota hai?",
        "What is polymorphism in OOP?",  # Out of scope
        "Explain deadlock in OS"  # Out of scope
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {clone.get_response(q)}\n")