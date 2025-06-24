from deepgram.utils import verboselogs
import os

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from functools import partial


class DeepgramTranscriber:
    """Transcriber for the zoom bot"""
    def __init__(self, message_callback):
        config = DeepgramClientOptions(options={"keepalive": "true"})
        self.message_callback = message_callback
        self.deepgram = DeepgramClient(os.environ.get('DEEPGRAM_API_KEY'), config)
        self.dg_connection = self.deepgram.listen.websocket.v("1") 

        self.current_sentence = []

        # Hook up the event handlers
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, partial(self._on_message))
        self.dg_connection.on(LiveTranscriptionEvents.Error, partial(self._on_error))
        self.dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, self._on_UtteranceEnd)

        options = LiveOptions(
            model="nova-3",
            # punctuate=True,
            interim_results=True,
            language='en-GB',
            encoding="linear16",
            sample_rate=32000,
            endpointing=2750,
            utterance_end_ms="1700",
            vad_events=True
        )

        self.dg_connection.start(options)
        self.speech_final_received = False

    def trim_tail(self, prev: str, curr: str) -> str:
        prev_words = prev.split()
        curr_words = curr.split()
        overlap_max = 0
        for i in range(1, min(len(prev_words), len(curr_words)) + 1):
            if prev_words[-i:] == curr_words[:i]:
                overlap_max = i
        return " ".join(curr_words[overlap_max:])

    def _on_message(self, client, result, **kwargs):
        transcript = result.channel.alternatives[0].transcript
        if getattr(result, "is_final", False):
            cleaned = self.trim_tail(" ".join(self.current_sentence), transcript)
            self.current_sentence.append(cleaned)

            if getattr(result, "speech_final", False):
                full_utterance = " ".join(self.current_sentence).strip()
                if not full_utterance:
                    return
                print(f"🟢Final Transcription🟢: {full_utterance}")
                self.current_sentence.clear()
                self.speech_final_received = True
                self.message_callback(full_utterance)
            else:
                self.speech_final_received = False

    def _on_UtteranceEnd(self, result, **kwargs):
        if not self.speech_final_received:
            full_utterance = " ".join(self.current_sentence).strip()
            if not full_utterance:
                return
            print(f"🔵Final Transcription (Triggered by UtteranceEnd)🔵: {full_utterance}")
            self.message_callback(full_utterance)
            self.current_sentence.clear()
        self.speech_final_received = True

    def _on_error(self, client, error, **kwargs):
        print(f"Error: {error}")

    def send(self, data):
        self.dg_connection.send(data)

    def finish(self):
        self.dg_connection.finish()
