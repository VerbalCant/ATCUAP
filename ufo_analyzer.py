from pathlib import Path
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import argparse
import sys
from datetime import datetime
import time
from tqdm import tqdm

class UFOAnalyzer:
    def __init__(self):
        # Load environment variables and get API key
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)
        
    def process_file(self, audio_path: Path, output_dir: Path) -> dict:
        """Process a single audio file and save results"""
        # Create output filename based on input filename
        stem = audio_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_base = output_dir / f"{stem}_{timestamp}"
        
        # Check for existing transcript with same stem
        existing_transcripts = list(output_dir.glob(f"{stem}_*.txt"))
        transcript_path = output_base.with_suffix('.txt')
        
        if existing_transcripts:
            # Use most recent transcript if it exists and is non-empty
            existing_transcript = max(existing_transcripts, key=lambda p: p.stat().st_mtime)
            if existing_transcript.stat().st_size > 0:
                print(f"\nFound existing transcript: {existing_transcript}")
                transcript = existing_transcript.read_text()
                transcript_path = existing_transcript
            else:
                # Proceed with transcription if existing file is empty
                transcript = self._transcribe_and_save(audio_path, transcript_path)
        else:
            # No existing transcript found, proceed with transcription
            transcript = self._transcribe_and_save(audio_path, transcript_path)
            
        print(f"Transcript length: {len(transcript)} characters")
        
        # Analyze
        print(f"Analyzing transcript for UFO phenomena...")
        analysis_start = time.time()
        analysis = self.analyze_transcript(transcript)
        analysis_time = time.time() - analysis_start
        
        # Save analysis
        analysis_path = output_base.with_suffix('.json')
        analysis_path.write_text(json.dumps(analysis, indent=2))
        print(f"Analysis saved to: {analysis_path}")
        print(f"Analysis completed in {analysis_time:.1f} seconds")
        
        return analysis

    def _transcribe_and_save(self, audio_path: Path, transcript_path: Path) -> str:
        """Helper method to handle transcription and saving"""
        # Get file size
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        print(f"\nProcessing {audio_path.name} ({file_size_mb:.1f} MB)")
        
        # Estimate processing time (rough estimate: ~12 seconds per MB)
        est_time = int(file_size_mb * 12)
        print(f"Estimated processing time: {est_time} seconds")
        
        # Transcribe with timer
        print(f"Transcribing {audio_path.name}...")
        transcript = self.transcribe_audio(audio_path, est_time)
        
        # Save transcript
        transcript_path.write_text(transcript)
        print(f"Transcript saved to: {transcript_path}")
        
        return transcript

    def transcribe_audio(self, audio_file_path, est_time):
        """Transcribe audio file using Whisper API"""
        start_time = time.time()
        
        # Start the transcription process
        with open(audio_file_path, "rb") as audio_file:
            # Start timer in a separate thread
            def update_timer():
                while True:
                    elapsed = time.time() - start_time
                    if elapsed >= est_time:
                        print(f"\rTranscribing... {elapsed:.1f}s (estimated: {est_time}s)", end="")
                    else:
                        remaining = est_time - elapsed
                        print(f"\rTranscribing... {elapsed:.1f}s (estimated: {est_time}s, remaining: {remaining:.1f}s)", end="")
                    time.sleep(0.1)
                    if elapsed > start_time + 120:  # Stop after 2 minutes of overrun
                        break

            from threading import Thread
            timer_thread = Thread(target=update_timer, daemon=True)
            timer_thread.start()

            # Perform transcription
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            
        elapsed = time.time() - start_time
        print(f"\nTranscription completed in {elapsed:.1f} seconds")
        
        return transcript

    def analyze_transcript(self, transcript):
        """Analyze transcript for UFO-related phenomena using GPT-4"""
        system_prompt = """You are a UFO/UAP research analyst. Your task is to analyze the provided transcript 
        and look for any mentions of:
        - Unidentified flying objects (UFOs)
        - Unidentified aerial phenomena (UAP)
        - Strange lights in the sky
        - Unexplained aerial events
        - Unusual atmospheric phenomena
        
        You must respond with a valid JSON object containing exactly these fields:
        {
            "has_phenomena": boolean,
            "summary": string or null
        }
        
        Example response for a positive match:
        {
            "has_phenomena": true,
            "summary": "At timestamp 2:15, the speaker reports seeing unexplained lights in formation"
        }
        
        Example response for no phenomena:
        {
            "has_phenomena": false,
            "summary": null
        }"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please analyze this transcript:\n\n{transcript}"}
                ],
                temperature=0.3  # Add lower temperature for more consistent formatting
            )
            
            content = response.choices[0].message.content.strip()
            print(f"\nRaw GPT response:\n{content}\n")  # Debug output
            
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse response as JSON: {e}")
                print("Attempting to fix common JSON formatting issues...")
                
                # Try to fix common formatting issues
                content = content.replace("'", '"')  # Replace single quotes with double quotes
                content = content.strip('`')  # Remove any markdown code block markers
                if content.startswith('json'):  # Remove any language identifier
                    content = content[4:].strip()
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    print("Failed to parse response even after fixes. Using default response.")
                    return {
                        "has_phenomena": False,
                        "summary": None,
                        "error": "Failed to parse GPT response"
                    }
                
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return {
                "has_phenomena": False,
                "summary": None,
                "error": f"Analysis error: {str(e)}"
            }

def main():
    parser = argparse.ArgumentParser(description='Analyze audio files for UFO/UAP phenomena')
    parser.add_argument('files', nargs='+', help='Audio files to analyze')
    parser.add_argument('-o', '--output', default='output',
                      help='Output directory for transcripts and analysis (default: output)')
    
    args = parser.parse_args()
    
    try:
        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        print(f"Output directory: {output_dir}")
        
        # Initialize analyzer
        analyzer = UFOAnalyzer()
        
        # Process each file with overall progress bar
        total_files = len(args.files)
        with tqdm(total=total_files, desc="Processing files", unit="file") as pbar:
            for i, file_path in enumerate(args.files, 1):
                file_path = Path(file_path)
                print(f"\nProcessing file {i} of {total_files}")
                print("=" * 50)
                
                if not file_path.exists():
                    print(f"Error: File not found: {file_path}")
                    pbar.update(1)
                    continue
                    
                try:
                    analysis = analyzer.process_file(file_path, output_dir)
                    
                    # Report findings
                    print(f"\nResults for {file_path.name}:")
                    if analysis["has_phenomena"]:
                        print("🛸 UFO/UAP PHENOMENA DETECTED!")
                        print("\nSummary of findings:")
                        print(analysis["summary"])
                    else:
                        print("No UFO/UAP phenomena detected in this recording.")
                    print("-" * 50)
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                
                pbar.update(1)
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 