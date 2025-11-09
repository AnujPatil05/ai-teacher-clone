from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

class VoiceClonerElevenLabs:
    def __init__(self):
        """Initialize ElevenLabs client"""
        self.client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY")
        )
        
        # Daniel voice for Hindi/English
        self.voice_id = "onwK4e9ZLuTAKqWW03F9"
        
        print(f"✓ ElevenLabs initialized with voice: {self.voice_id}")
    
    def generate_voice(self, text, output_path="static/response.wav"):
        """Generate speech from text"""
        try:
            print(f"🎤 Generating audio with ElevenLabs...")
            
            # Correct method using client.text_to_speech
            audio = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2"
            )
            
            # Save audio - audio is a generator of bytes
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Audio saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ ElevenLabs error: {e}")
            return None
    
    def list_available_voices(self):
        """List all available voices"""
        try:
            response = self.client.voices.get_all()
            print("\n📋 Available Voices:")
            for voice in response.voices:
                print(f"  - {voice.name}: {voice.voice_id}")
            return response
        except Exception as e:
            print(f"Error listing voices: {e}")
            return None


# Test
if __name__ == "__main__":
    cloner = VoiceClonerElevenLabs()
    
    print("\n" + "="*50)
    cloner.list_available_voices()
    print("="*50 + "\n")
    
    test_text = "Namaste students! Aaj hum DBMS ke normalization ke baare mein seekhenge. Yeh concept bahut important hai."
    
    result = cloner.generate_voice(test_text, "static/test_elevenlabs.wav")
    
    if result:
        print(f"\n✅ Success! Play: {result}")