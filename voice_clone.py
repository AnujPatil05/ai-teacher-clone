from TTS.api import TTS
import torch
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
import os

class VoiceCloner:
    def __init__(self):
        # Setup device and allowlist XTTS configs
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        torch.serialization.add_safe_globals([
            XttsConfig,
            XttsAudioConfig,
            BaseDatasetConfig,
            XttsArgs
        ])

        # Load XTTS model for voice cloning
        self.xtts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)

        # Load Coqui Hindi TTS model for fallback
        self.fallback = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        


        # Reference audio for cloning
        self.reference_audio = r"D:\teacher-clone-ai\videos\Biggest CyberAttack in the History ｜ Why Cybersecurity🕵️‍♀️🕵️‍♂️ is Very Important🔝？.wav"

    def clone_voice(self, text, output_path="static/cloned.wav"):
        console = Console()
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Cloning voice...", total=None)

            self.xtts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=self.reference_audio,
                temperature=0.7,
                repetition_penalty=2.0,
                language="hi"
            )
        return output_path

    def fallback_voice(self, text, output_path="static/fluent.wav"):
        console = Console()
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Generating fluent Hindi voice...", total=None)

            # Choose a valid speaker from the model
            
            self.fallback.tts_to_file(
                text=text,
                file_path=output_path,
                language="hi"
            )
        return output_path



# 🧪 Interactive CLI
if __name__ == "__main__":
    console = Console()
    cloner = VoiceCloner()

    console.print("[bold cyan]Choose voice mode:[/bold cyan]")
    console.print("1. Clone teacher's voice")
    console.print("2. Use fluent Hindi voice")
    console.print("3. Generate both")

    choice = input("Enter 1, 2, or 3: ").strip()
    text = input("Enter the text to synthesize: ").strip()

    os.makedirs("static", exist_ok=True)
    

    if choice == "1":
        cloner.clone_voice(text)
        console.print("[green]✅ Cloned voice saved to static/cloned.wav[/green]")
    elif choice == "2":
        cloner.fallback_voice(text)
        console.print("[green]✅ Fluent voice saved to static/fluent.wav[/green]")
    elif choice == "3":
        cloner.clone_voice(text)
        cloner.fallback_voice(text)
        console.print("[green]✅ Both voices saved: cloned.wav and fluent.wav[/green]")
    else:
        console.print("[red]Invalid choice. Please enter 1, 2, or 3.[/red]")