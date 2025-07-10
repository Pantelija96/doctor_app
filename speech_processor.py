import pyaudio
import whisper
import numpy as np
import threading
import torch
import time
import logging
import os
import wave
import datetime
from PyQt6.QtCore import pyqtSignal, QObject

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

class SpeechProcessor(QObject):
    transcription_completed = pyqtSignal(str, str)  # Signal for (audio_path, text)

    def __init__(self, audio_dir):
        super().__init__()
        self.audio_dir = audio_dir
        os.makedirs(self.audio_dir, exist_ok=True)
        self.model = None
        self.recording = False
        self.frames = []
        self.stop_event = None
        self.recording_thread = None
        try:
            self.model = whisper.load_model("medium")
            logging.info(f"Whisper model 'medium' loaded. CUDA available: {torch.cuda.is_available()}")
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            self.transcription_completed.emit(None, "Failed to load Whisper model.")

    def record_audio(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            logging.info("Recording started...")
            while not self.stop_event.is_set():
                data = stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
            stream.stop_stream()
            stream.close()
            p.terminate()
            logging.info(f"Recording stopped, captured {len(self.frames)} frames")
        except Exception as e:
            logging.error(f"Recording failed: {e}")
            self.stop_event.set()
            self.transcription_completed.emit(None, f"Recording failed: {str(e)}")

    def start_recording(self):
        if self.recording or not self.model:
            logging.warning("Cannot start recording: already recording or model not loaded")
            return False
        self.recording = True
        self.frames = []
        self.stop_event = threading.Event()
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()
        logging.info("Recording thread started")
        return True

    def stop_recording(self):
        if not self.recording:
            logging.warning("Cannot stop recording: not recording")
            return None, None
        try:
            self.stop_event.set()
            self.recording_thread.join()
            self.recording = False
            # Save audio to file
            audio_path = os.path.join(self.audio_dir, f"recording_{int(datetime.datetime.now().timestamp())}.wav")
            wf = wave.open(audio_path, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b"".join(self.frames))
            wf.close()
            file_size = os.path.getsize(audio_path)
            logging.info(f"Audio saved to {audio_path}, size: {file_size} bytes")
            # Transcribe
            audio_data = b"".join(self.frames)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            start_time = time.time()
            result = self.model.transcribe(audio=audio_np, language="sr", fp16=torch.cuda.is_available())
            transcription_time = time.time() - start_time
            text = result["text"].strip()
            if text:
                # Convert to Serbian Latin
                text = cyrillic_to_latin(text)
                logging.info(f"Transcription (Latin): {text}")
                logging.info(f"Transcription took {transcription_time:.2f} seconds")
            else:
                logging.warning("Transcription resulted in empty text")
                text = "Transkripcija nije uspela."
            self.transcription_completed.emit(audio_path, text)
            return audio_path, text
        except Exception as e:
            logging.error(f"Stop recording or transcription failed: {e}")
            self.transcription_completed.emit(None, f"Transkripcija nije uspela: {str(e)}")
            return None, None