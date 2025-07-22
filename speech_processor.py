import os
import sys
import whisper
import pyaudio
import numpy as np
import threading
import torch
import wave
import datetime
from PyQt6.QtCore import pyqtSignal, QObject
import torchaudio
import logging

# Ensure audio directory exists before logging setup
def get_audio_dir(base_dir):
    appdata_path = os.getenv('APPDATA') or os.path.expanduser('~/AppData/Roaming')
    audio_dir = os.path.join(appdata_path, 'DoctorApp', base_dir)
    os.makedirs(audio_dir, exist_ok=True)
    return audio_dir

# Set up logging after creating audio directory
audio_dir = get_audio_dir('audio')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(os.path.join(audio_dir, 'app.log'))]
)

# Set FFmpeg path
if getattr(sys, 'frozen', False):
    os.environ["PATH"] += os.pathsep + sys._MEIPASS
    torchaudio.set_audio_backend("ffmpeg")

# Serbian Cyrillic to Latin mapping
CYRILLIC_TO_LATIN = {
    'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v', 'Г': 'G', 'г': 'g',
    'Д': 'D', 'д': 'd', 'Ђ': 'Đ', 'ђ': 'đ', 'Е': 'E', 'е': 'e', 'Ж': 'Ž', 'ж': 'ž',
    'З': 'Z', 'з': 'z', 'И': 'I', 'и': 'i', 'Ј': 'J', 'ј': 'j', 'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l', 'Љ': 'Lj', 'љ': 'lj', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n',
    'Њ': 'Nj', 'њ': 'nj', 'О': 'O', 'о': 'o', 'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's', 'Т': 'T', 'т': 't', 'Ћ': 'Ć', 'ћ': 'ć', 'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f', 'Х': 'H', 'х': 'h', 'Ц': 'C', 'ц': 'c', 'Ч': 'Č', 'ч': 'č',
    'Џ': 'Dž', 'џ': 'dž', 'Ш': 'Š', 'ш': 'š'
}

def cyrillic_to_latin(text):
    return ''.join(CYRILLIC_TO_LATIN.get(char, char) for char in text)

def resource_path(relative_path):
    base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_model_path(model_name):
    return resource_path(f'whisper/assets/{model_name}.pt')

class SpeechProcessor(QObject):
    transcription_completed = pyqtSignal(str, str)  # (text, audio_path)

    def __init__(self, audio_dir):
        super().__init__()
        self.audio_dir = get_audio_dir(audio_dir)
        self.model = None
        self.recording = False
        self.frames = []
        self.stop_event = None
        self.recording_thread = None
        try:
            model_path = get_model_path("small")
            self.model = whisper.load_model(model_path)
            logging.info(f"Whisper model 'small' loaded. CUDA: {torch.cuda.is_available()}")
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            self.transcription_completed.emit(None, f"Failed to load Whisper model: {str(e)}")

    def start_recording(self):
        try:
            if self.recording:
                return False
            self.recording = True
            self.frames = []
            self.stop_event = threading.Event()
            self.recording_thread = threading.Thread(target=self._record)
            self.recording_thread.start()
            return True
        except Exception as e:
            logging.error(f"Error starting recording: {e}")
            self.transcription_completed.emit(None, f"Failed to start recording: {str(e)}")
            return False

    def _record(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
            while self.recording and not self.stop_event.is_set():
                data = stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            logging.error(f"Error during recording: {e}")
            self.transcription_completed.emit(None, f"Recording failed: {str(e)}")

    def stop_recording(self):
        try:
            if not self.recording:
                return None, "No recording to stop."
            self.recording = False
            self.stop_event.set()
            self.recording_thread.join()
            audio_file = os.path.join(self.audio_dir, f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
            wf = wave.open(audio_file, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            logging.info(f"Audio saved to: {audio_file}")
            text = self.transcribe(audio_file)
            return audio_file, text
        except Exception as e:
            logging.error(f"Error stopping recording: {e}")
            self.transcription_completed.emit(None, f"Failed to save audio: {str(e)}")
            return None, f"Failed to save audio: {str(e)}"

    def transcribe(self, audio_file):
        try:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            result = self.model.transcribe(audio_file, language="sr", verbose=True)
            text = result["text"]
            latin_text = cyrillic_to_latin(text)
            logging.info(f"Transcription result: {latin_text}")
            self.transcription_completed.emit(latin_text, audio_file)
            return latin_text
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            self.transcription_completed.emit(None, f"Transcription failed: {str(e)}")
            return f"Transcription failed: {str(e)}"