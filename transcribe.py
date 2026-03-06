"""Simple VOSK transcription helper.

Record from the default microphone or read a WAV file and print the final text.

Usage examples:
    pip install -r requirements.txt
    # download a model first: https://alphacephei.com/vosk/models
    python transcribe.py --model /path/to/vosk-model-small-en-us
    python transcribe.py --model /path/to/vosk-model-small-en-us --file order.wav
    python transcribe.py --model /path/to/vosk-model-small-en-us --mic
"""
import argparse
import json

from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import sys
import wave

q = queue.Queue()


def record_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def transcribe_file(model_path: str, wav_path: str):
    wf = wave.open(wav_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
        raise ValueError("Input WAV must be mono PCM 16-bit")
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    result = None
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
    final = rec.FinalResult()
    print(final)
    return final


def transcribe_mic(model_path: str, samplerate: int = 16000):
    model = Model(model_path)
    rec = KaldiRecognizer(model, samplerate)

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype="int16",
                            channels=1, callback=record_callback):
        print("Listening... press Ctrl-C to stop")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                print(rec.Result())
            else:
                print(rec.PartialResult())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="path to vosk model directory")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="WAV file to transcribe")
    group.add_argument("--mic", action="store_true", help="use microphone input")
    args = parser.parse_args()

    if args.file:
        transcribe_file(args.model, args.file)
    elif args.mic:
        transcribe_mic(args.model)


if __name__ == "__main__":
    main()
