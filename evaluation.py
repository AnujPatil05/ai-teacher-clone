import json
import time
from datetime import datetime
from chatbot import TeacherClone
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class ChatbotEvaluator:
    def __init__(self):
        self.teacher_clone = TeacherClone()
        self.evaluator_model = genai.GenerativeModel('gemini-1.5-flash')
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'metrics': {}
        }
    
    def evaluate_response_quality(self, question, response, expected_topics):
        """
        Evaluate if response covers expected topics and maintains teaching style
        """
        evaluation_prompt = f"""
Evaluate this AI teacher's response on a scale of 1-10:

Question: {question}

Response: {response}

Expected topics to cover: {expected_topics}

Evaluate based on:
1. **Accuracy** (1-10): Are the concepts explained correctly?
2. **Completeness** (1-10): Does it cover the expected topics?
3. **Teaching Style** (1-10): Does it match Gate Smashers' style (Hinglish, enthusiastic, step-by-step)?
4. **Clarity** (1-10): Is the explanation clear and easy to understand?
5. **Engagement** (1-10): Is it engaging and encouraging?

Return ONLY a JSON object with these scores:
{{"accuracy": X, "completeness": X, "teaching_style": X, "clarity": X, "engagement": X}}
"""
        
        try:
            result = self.evaluator_model.generate_content(evaluation_prompt)
            # Parse JSON from response
            response_text = result.text.strip()
            # Extract JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            scores = json.loads(response_text)
            return scores
        except Exception as e:
            print(f"Evaluation error: {e}")
            return None
    
    def measure_response_time(self, question):
        """Measure response generation time"""
        start_time = time.time()
        response = self.teacher_clone.get_response(question)
        end_time = time.time()
        
        response_time = end_time - start_time
        return response, response_time
    
    def evaluate_rag_retrieval(self, question, response):
        """Check if RAG successfully retrieved relevant context"""
        # Check if response uses context from lectures
        check_prompt = f"""
Does this response use specific information from lecture content, or is it generic knowledge?

Question: {question}
Response: {response}

Answer with JSON:
{{"uses_lecture_context": true/false, "confidence": 0-10}}
"""
        
        try:
            result = self.evaluator_model.generate_content(check_prompt)
            response_text = result.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            rag_result = json.loads(response_text)
            return rag_result
        except Exception as e:
            print(f"RAG evaluation error: {e}")
            return None
    
    def run_test_suite(self):
        """Run comprehensive test suite"""
        
        # Test cases: (question, expected_topics, is_in_scope)
        test_cases = [
            {
                "question": "DBMS mein normalization kya hai?",
                "expected_topics": "normalization, normal forms, database design, redundancy",
                "category": "In-Scope (DBMS)",
                "in_scope": True
            },
            {
                "question": "Explain ACID properties in database",
                "expected_topics": "Atomicity, Consistency, Isolation, Durability, transactions",
                "category": "In-Scope (DBMS)",
                "in_scope": True
            },
            {
                "question": "What is deadlock in operating systems?",
                "expected_topics": "deadlock, resource allocation, circular wait, OS concepts",
                "category": "Out-of-Scope (OS)",
                "in_scope": False
            },
            {
                "question": "Explain polymorphism in OOP",
                "expected_topics": "polymorphism, compile-time, runtime, method overriding, overloading",
                "category": "Out-of-Scope (OOP)",
                "in_scope": False
            },
            {
                "question": "What is indexing in DBMS?",
                "expected_topics": "indexing, B-tree, search optimization, database performance",
                "category": "In-Scope (DBMS)",
                "in_scope": True
            }
        ]
        
        print("\n" + "="*60)
        print("🧪 STARTING EVALUATION TEST SUITE")
        print("="*60 + "\n")
        
        total_scores = {
            'accuracy': [],
            'completeness': [],
            'teaching_style': [],
            'clarity': [],
            'engagement': [],
            'response_times': [],
            'rag_success': []
        }
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n[Test {i}/{len(test_cases)}] Category: {test['category']}")
            print(f"Question: {test['question']}")
            print("-" * 60)
            
            # Measure response time
            response, response_time = self.measure_response_time(test['question'])
            print(f"⏱️  Response Time: {response_time:.2f} seconds")
            print(f"📝 Response Preview: {response[:150]}...")
            
            # Evaluate quality
            scores = self.evaluate_response_quality(
                test['question'], 
                response, 
                test['expected_topics']
            )
            
            if scores:
                print(f"\n📊 Quality Scores:")
                print(f"   Accuracy: {scores['accuracy']}/10")
                print(f"   Completeness: {scores['completeness']}/10")
                print(f"   Teaching Style: {scores['teaching_style']}/10")
                print(f"   Clarity: {scores['clarity']}/10")
                print(f"   Engagement: {scores['engagement']}/10")
                
                # Add to totals
                for key in ['accuracy', 'completeness', 'teaching_style', 'clarity', 'engagement']:
                    total_scores[key].append(scores[key])
            
            # Evaluate RAG
            if test['in_scope']:
                rag_result = self.evaluate_rag_retrieval(test['question'], response)
                if rag_result:
                    print(f"\n🔍 RAG Evaluation:")
                    print(f"   Uses Lecture Context: {rag_result['uses_lecture_context']}")
                    print(f"   Confidence: {rag_result['confidence']}/10")
                    total_scores['rag_success'].append(1 if rag_result['uses_lecture_context'] else 0)
            
            total_scores['response_times'].append(response_time)
            
            # Store result
            self.results['tests'].append({
                'question': test['question'],
                'category': test['category'],
                'response': response,
                'response_time': response_time,
                'scores': scores,
                'in_scope': test['in_scope']
            })
            
            print("\n" + "="*60)
        
        # Calculate averages
        self.results['metrics'] = {
            'avg_accuracy': sum(total_scores['accuracy']) / len(total_scores['accuracy']) if total_scores['accuracy'] else 0,
            'avg_completeness': sum(total_scores['completeness']) / len(total_scores['completeness']) if total_scores['completeness'] else 0,
            'avg_teaching_style': sum(total_scores['teaching_style']) / len(total_scores['teaching_style']) if total_scores['teaching_style'] else 0,
            'avg_clarity': sum(total_scores['clarity']) / len(total_scores['clarity']) if total_scores['clarity'] else 0,
            'avg_engagement': sum(total_scores['engagement']) / len(total_scores['engagement']) if total_scores['engagement'] else 0,
            'avg_response_time': sum(total_scores['response_times']) / len(total_scores['response_times']),
            'rag_success_rate': (sum(total_scores['rag_success']) / len(total_scores['rag_success']) * 100) if total_scores['rag_success'] else 0,
            'total_tests': len(test_cases)
        }
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def print_summary(self):
        """Print evaluation summary"""
        print("\n" + "="*60)
        print("📈 EVALUATION SUMMARY")
        print("="*60)
        
        metrics = self.results['metrics']
        
        print(f"\n🎯 Overall Scores (out of 10):")
        print(f"   Accuracy:        {metrics['avg_accuracy']:.2f}/10")
        print(f"   Completeness:    {metrics['avg_completeness']:.2f}/10")
        print(f"   Teaching Style:  {metrics['avg_teaching_style']:.2f}/10")
        print(f"   Clarity:         {metrics['avg_clarity']:.2f}/10")
        print(f"   Engagement:      {metrics['avg_engagement']:.2f}/10")
        
        overall_avg = (
            metrics['avg_accuracy'] + 
            metrics['avg_completeness'] + 
            metrics['avg_teaching_style'] + 
            metrics['avg_clarity'] + 
            metrics['avg_engagement']
        ) / 5
        
        print(f"\n   📊 Overall Average: {overall_avg:.2f}/10 ({overall_avg * 10:.1f}%)")
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Avg Response Time: {metrics['avg_response_time']:.2f} seconds")
        print(f"   RAG Success Rate:  {metrics['rag_success_rate']:.1f}%")
        print(f"   Total Tests Run:   {metrics['total_tests']}")
        
        print("\n" + "="*60 + "\n")
    
    def save_results(self):
        """Save evaluation results to JSON"""
        filename = f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"💾 Results saved to: {filename}")


# Run evaluation
if __name__ == "__main__":
    print("\n🚀 Starting AI Teacher Clone Evaluation...")
    print("This will take a few minutes...\n")
    
    evaluator = ChatbotEvaluator()
    results = evaluator.run_test_suite()
    
    print("\n✅ Evaluation complete!")
    print(f"Check the JSON file for detailed results.")