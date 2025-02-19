#!/usr/bin/env python
import os
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
import requests
from pydub import AudioSegment
from pydub.utils import make_chunks
from pathlib import Path
import assemblyai as aai
from crews.meeting_minutes_crew.meeting_minutes_crew import MeetingMinutesCrew
load_dotenv()


class MeetingsMinutesState(BaseModel):
    transcript: str = ""
    meeting_minutes: str = ""


class meetingMinutesFlow(Flow[MeetingsMinutesState]):

    @start()
    def transcribe_meeting(self):
        print("Generating Transcription")

        SCRIPT_DIR = Path(__file__).parent
        audio_path = str(SCRIPT_DIR / "EarningsCall.wav")
        
        # Load the audio file
        audio = AudioSegment.from_file(audio_path, format="wav")
        
        # Define chunk length in milliseconds (e.g., 1 minute = 60,000 ms)
        chunk_length_ms = 60000
        chunks = make_chunks(audio, chunk_length_ms)

        # Transcribe each chunk
        full_transcription = ""
        
        # Whisper API Endpoint
        url = "https://api.assemblyai.com/v2/transcripts"
        headers = {
        "Authorization": os.getenv("ASSEMBLY_API_KEY"),
        }

        # AssemblyAI API Endpoint
        aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY")
        transcriber = aai.Transcriber()
        
        for i, chunk in enumerate(chunks):
            print(f"Transcribing chunk {i+1}/{len(chunks)}")
            chunk_path = f"chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")

            # SCRIPT_DIR_CHUNK = Path('/Users/zap/Desktop/multi-agent-crewai/meeting_minutes')
            # str(SCRIPT_DIR_CHUNK / f"chunk_{i}.wav")

            # with open(chunk_path, "rb") as audio_file:
            #     print(audio_file)
            #     files = {
            #         "file": audio_file
            #     }
            #     data = {
            #         "language": "english",
            #         "response_format": "json"
            #     }
                
            #     transcription = requests.post(url, headers=headers, files=files, data=data)
            #     print(f"successfuly transcribe chunk {i+1}/{len(chunks)}")

            transcription = transcriber.transcribe(chunk_path)
            print(transcription)

                
            full_transcription += transcription.text + " "
            
 
        self.state.transcript = full_transcription
        print(f"Transcription: {self.state.transcript}")
        
    @listen(transcribe_meeting)
    def generate_meeting_minutes(self):
        print("Generating Meeting Minutes")

        crew = MeetingMinutesCrew()

        inputs = {
            "transcript": self.state.transcript
        }
        meeting_minutes = crew.crew().kickoff(inputs)
        self.state.meeting_minutes = meeting_minutes

    @listen(generate_meeting_minutes)
    def create_draft_meeting_minutes(self):
        print("Creating Draft Meeting Minutes")

        

def kickoff():
    meeting_minutes_flow = meetingMinutesFlow()
    meeting_minutes_flow.kickoff()



if __name__ == "__main__":
    kickoff()
