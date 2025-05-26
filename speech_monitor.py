import json
import pyaudio
from vosk import Model, KaldiRecognizer
from typing import Dict, Set, Callable, Optional

import os
from pathlib import Path
from dotenv import load_dotenv

from pynput.keyboard import Controller as KeyboardController, Key
import time


class SpeechMonitor:
    def __init__(self, model_path: str, forbidden_words: set, 
                 sample_rate: int = 16000, buffer_size: int = 4096,
                 warning_text :str ='\033[1;31m', reset_text :str ='\033[0m'):
        """
        Initialize the speech monitor with configuration settings.
        
        Args:
            model_path: Path to Vosk model
            forbidden_words: Dictionary of words to monitor with initial detection status
            sample_rate: Audio sample rate
            buffer_size: Audio buffer size
        """
        self.MODEL_PATH = model_path
        self.SAMPLE_RATE = sample_rate
        self.BUFFER_SIZE = buffer_size
        self.FORBIDDEN_WORDS = forbidden_words.copy()
        self.detected_words: Set[str] = set()
        self.WARNING_TEXT = warning_text
        self.RESET_TEXT = reset_text

        self.audio_list = []

        # Audio stream components
        self.recognizer: Optional[KaldiRecognizer] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.mic: Optional[pyaudio.PyAudio] = None
        
        # Callback management
        self.callbacks: Dict[str, Callable] = {}
        
    def initialize_audio_stream(self) -> None:
        """Initialize the audio stream and Vosk recognizer."""
        try:
            model = Model(self.MODEL_PATH)
            self.recognizer = KaldiRecognizer(model, self.SAMPLE_RATE)
            
            self.mic = pyaudio.PyAudio()
            self.stream = self.mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.BUFFER_SIZE,
                input_device_index=0
            )

        except Exception as e:
            print(f"Initialization failed: {e}")
            raise

    def register_callback(self, word: str, callback: Callable[..., None]) -> None:
        """Register a callback for the accepted word."""
        self.callbacks[word] = callback


    def _execute_callbacks(self, word: str) -> None:
        """Execute the appropriate callback for a detected word."""
        callback = self.callbacks.get(word)
        if callback:
            callback()
    
    def _info(self, current_sentence:str,mode:str = "full") -> None:
        """Prints the sentence with forbidden word fragments highlighted."""


        words = current_sentence.split()
        for i, word in enumerate(words):
            lower_word = word.lower()
            for forbidden in self.FORBIDDEN_WORDS:
                if forbidden in lower_word:
                    if (lower_word == forbidden.lower()) and (mode == "full"):
                    # Highlight the entire word
                        words[i] = f"{self.WARNING_TEXT}{word}{self.RESET_TEXT}"
                        break
                    # Highlight only the forbidden portion
                    if (mode == "partial"):
                        words[i] = word.replace(
                            forbidden, 
                            f"{self.WARNING_TEXT}{forbidden}{self.RESET_TEXT}"
                        )
                        break

        print(' '.join(words))  # Print reconstructed sentence

    def _process_partial_result_and_full_result(self, text: str, mode: str) -> str:
        """Process a complete sentence mode and partial mode."""
        
        current_line = text.lower()
        new_detections = set()
        self.detected_words.clear()  # Reset for next utterance

        for word in self.FORBIDDEN_WORDS:
            if " "+ word + " " in  " " + current_line +" " and word and mode == "full" not in self.detected_words:
                new_detections.add(word)
                self._execute_callbacks(word)
                

            if word in current_line and word and mode == "partial" not in self.detected_words:
                new_detections.add(word)
                self._execute_callbacks(word)
                
        if new_detections:
            self.detected_words.update(new_detections)
            

        return current_line
  
  
    def output_audio(self) -> list:
        
        return self.audio_list.copy()    

    def monitor_speech(self, mode: str):
        """
        Monitor speech using the specified detection mode.
        
        Args:
            mode: Detection mode ('full', 'partial')
        """

        if not all([self.recognizer, self.stream, self.mic]):
            self.initialize_audio_stream()
            # Validate mode first

        if mode not in ("full", "partial"):
            raise ValueError(f"Invalid mode: {mode}. Use 'full', 'partial'")


        print(f"Listening for forbidden words -> mode... (Press Ctrl+C to stop)")
        
        current_line = ""

        try:
            while True:
                data = self.stream.read(self.BUFFER_SIZE, exception_on_overflow=False)
                

                # Process audio data
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if "text" in result:
                        if mode in ("full"):
                            current_line = self._process_partial_result_and_full_result(result["text"], mode)
                        if mode in ("partial"):
                            current_line = self._process_partial_result_and_full_result(result["text"], mode)

                    self.audio_list.append(current_line)
                    self._info(current_line,mode)

        
        except KeyboardInterrupt:
            print("\nStopping...")
        except Exception as e:
            print(f"Error during processing: {e}")
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Clean up audio resources."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.mic:
            self.mic.terminate()

def get_config():
    """Returns config with environment-aware paths"""
    config = {
        "model_path": os.getenv('VOSK_MODEL_PATH'),
        "forbidden_words": {
            "forward", "backward", "left", "right",
            "roll", "dash", "matrix", "attack",
            "drink", "heal", "potion", "lock",
            "enemy", "run", "stop"
        }
    }
    
    if not config["model_path"]:
        raise ValueError("VOSK_MODEL_PATH not set in .env file")
    return config

# Example usage
if __name__ == "__main__":

    # Load environment variables
    load_dotenv()

    CONFIG = get_config()

    # Create monitor instance
    monitor = SpeechMonitor(**CONFIG)
    keyboard = KeyboardController()
    
    # Register custom callbacks
    def forward_callback():
        keyboard.press('w')
        time.sleep(3)
        keyboard.release('w')
    
    def backward_callback():
        keyboard.press('s')
        time.sleep(3)
        keyboard.release('s')

    def left_callback():
        keyboard.press('a')
        time.sleep(3)
        keyboard.release('a')

    def right_callback():
        keyboard.press('d')
        time.sleep(3)
        keyboard.release('d')

    def dash_forward_callback():
        keyboard.press('w')       
        time.sleep(0.1)           
        keyboard.press(Key.space) 
        time.sleep(0.2)           
        keyboard.release(Key.space) 
        time.sleep(0.1)           
        keyboard.release('w')

    def enter_callback():
        keyboard.press('e')
        time.sleep(0.2)
        keyboard.release('e')
        time.sleep(0.1) 
    
    def attack_callback():
        keyboard.press('p')
        time.sleep(0.2)
        keyboard.release('p')
        time.sleep(0.1) 
    
    def drink_callback():
        keyboard.press('r')
        time.sleep(0.2)
        keyboard.release('r')
        time.sleep(0.1) 
    
    def lock_callback():
        keyboard.press('q')
        time.sleep(0.2)
        keyboard.release('q')
        time.sleep(0.1) 

        

    monitor.register_callback("forward", forward_callback)
    monitor.register_callback("backward", backward_callback)
    monitor.register_callback("right",right_callback)
    monitor.register_callback("left",left_callback)
    monitor.register_callback("roll", dash_forward_callback)
    monitor.register_callback("dash", dash_forward_callback)
    monitor.register_callback("matrix", enter_callback)
    monitor.register_callback("drink", drink_callback)
    monitor.register_callback("heal", drink_callback)
    monitor.register_callback("potion", drink_callback)
    monitor.register_callback("lock", lock_callback)
    monitor.register_callback("enemy", lock_callback)
    monitor.register_callback("attack", attack_callback)
    
    # Start monitoring
    monitor.monitor_speech(mode="full")