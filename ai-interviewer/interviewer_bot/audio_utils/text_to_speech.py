import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from openai._response import AsyncStreamedBinaryAPIResponse
import os
import numpy as np
from scipy.signal import resample_poly
load_dotenv()
openai = AsyncOpenAI(api_key=os.environ.get("OPENAI-API-KEY"))

def resample_pcm_24k_to_32k(pcm_bytes: bytes) -> bytes:
  '''
    Takes in 24k pcm and resamples to 32k to be playable in zoom

    Parameters:
      pcm_bytes: bytes
        pcm bytes from the async api client
    Returns: 
      32k pcm byte stream
  '''
  audio_24k = np.frombuffer(pcm_bytes, dtype='<i2')  

  audio_32k = resample_poly(audio_24k, up=4, down=3)

  audio_32k = np.clip(audio_32k, -32768, 32767).astype('<i2')

  return audio_32k.tobytes()

async def text_to_audio(text: str,callback: callable) -> None:
  '''
  Creates an api stream to read a string

      Parameters:
        text: str 
            text to serve as the input to the bot.
        callback: callable 
            function used to play the audio to
      Returns: 
        None
  '''

  async with openai.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input=text,
    response_format="pcm",
  ) as response:
    await asyncio.sleep(1) # Note: this is needed to buffer some audio to ensure a non static response
    await play_stream(response, callback)

async def play_stream(audio_bytes:AsyncStreamedBinaryAPIResponse, callback:callable) -> None:
  '''
    Takes the audio, reads it out, resamples the data and sends it to the callback function

    Parameters:
      audio_bytes 
          async api bytes of audio 
      callback: callable 
          function used to play the audio to
    Returns: 
      None
  '''
  leftover = b""
  buffer = b""
  async for raw in audio_bytes.iter_bytes():
    data = leftover + raw
    if len(data) % 2:
      leftover = data[-1:]
      data = data[:-1]
    else:
      leftover = b""
    buffer += data

    while len(buffer) >= 960:
      chunk = buffer[:960]
      buffer = buffer[960:]

      resampled = resample_pcm_24k_to_32k(chunk)
      callback(resampled, 32000)

      await asyncio.sleep(0.0125)
  if buffer: 
    pad_len = 960 - len(buffer)
    padded = buffer + b'\x00' * pad_len
    resampled = resample_pcm_24k_to_32k(padded)
    callback(resampled, 32000)
    await asyncio.sleep(0.0125)




