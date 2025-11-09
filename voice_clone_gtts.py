from gtts import gTTS
import os
from pydub import AudioSegment



class VoiceClonerGTTS:
    def __init__(self):
        """Initialize Google Text-to-Speech (Free, No API key, No restrictions)"""
        print("✓ Google TTS initialized (Free, unlimited)")
        
    @staticmethod    
    def speed_up_audio(path, factor=1.15):
        sound = AudioSegment.from_file(path)
        faster = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * factor)
        }).set_frame_rate(sound.frame_rate)
        faster.export(path, format="mp3")
    
    def generate_voice(self, text, output_path="static/response.mp3"):
        """Generate speech using Google TTS"""
        try:
            print(f"🎤 Generating audio with Google TTS...")
            
            # Generate audio (supports Hindi + English mixing perfectly)
            tts = gTTS(
                text=text,
                lang='hi',  # Hindi language (handles Hinglish well)
                slow=False,
                lang_check=False  # Allow mixed languages
            )
            
            # Save audio
            tts.save(output_path)
            self.speed_up_audio(output_path, factor=1.25)

            print(f"✅ Audio saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error: {e}")
            # Try English as fallback
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(output_path)
                print(f"✅ Audio saved (English): {output_path}")
                return output_path
            except:
                return None
     


        

# Test
if __name__ == "__main__":
    cloner = VoiceClonerGTTS()
    
    # Test with Hinglish
    test_text = "Namaste students! Aaj hum DBMS ke normalization ke baare mein seekhenge. Yeh concept bahut important hai database design ke liye."
    
    result = cloner.generate_voice(test_text, "static/test_gtts.mp3")
    
    if result:
        print(f"\n✅ SUCCESS! Play the file: {result}")
        print("Audio should work perfectly in your web app!")
    else:
        print("\n❌ Failed")