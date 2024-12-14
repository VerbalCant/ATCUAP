# UFO Analyzer

A Python tool that analyzes audio recordings for mentions of UFO/UAP phenomena. This tool:
1. Transcribes audio files using OpenAI's Whisper API
2. Analyzes the transcripts using GPT-4o to detect mentions of:
   - Unidentified flying objects (UFOs)
   - Unidentified aerial phenomena (UAP)
   - Strange lights in the sky
   - Unexplained aerial events
   - Unusual atmospheric phenomena

## Requirements

- Python 3.8 or higher
- OpenAI API key
- Audio files in supported formats (mp3, mp4, mpeg, mpga, m4a, wav, or webm)
- Maximum file size: 25 MB per file (Whisper API limit)
- tqdm (for progress bars)

## Installation

1. Clone this repository:

```
bash
git clone https://github.com/yourusername/ufo-analyzer.git
cd ufo-analyzer
```

2. Install the package:

```
bash
pip install -r requirements.txt
```

3. Set your OpenAI API key:

```
bash
export OPENAI_API_KEY=your_api_key
# Either export in your shell:
export OPENAI_API_KEY=your_api_key

# Or create a .env file:
echo "OPENAI_API_KEY=your_api_key" > .env
```

## Usage

```
bash
python ufo_analyzer.py <path_to_audio_files>
```

This will transcribe the audio files and analyze them for UFO/UAP phenomena. The results will be saved in a JSON file with the same name as the audio file, in the same directory.

Specify custom output directory with -o flag:

```
bash
python ufo_analyzer.py -o <path_to_output_directory> <path_to_audio_files>
```

## Output

The tool creates two files for each processed audio file:
- `{filename}_{timestamp}.txt`: The transcript from Whisper
- `{filename}_{timestamp}.json`: The UFO/UAP analysis from GPT-4o

If a transcript already exists for an audio file (with the same stem name), it will be reused instead of making a new API call. This saves time and API costs on subsequent runs.

### Example Output Structure

```
output/
├── recording1_20240315_123456.txt    # Transcript
├── recording1_20240315_123456.json   # Analysis
├── recording2_20240315_123457.txt
└── recording2_20240315_123457.json
```

### Analysis Results

The JSON analysis file contains:
- `has_phenomena`: Boolean indicating if UFO/UAP phenomena were detected
- `summary`: If phenomena were detected, a summary of the findings
- `error`: (if present) Indicates any issues during analysis

Example:
```json
{
  "has_phenomena": true,
  "summary": "At timestamp 2:15, the speaker reports seeing unexplained lights in formation"
}
```

## Performance Notes

- Transcription time varies with file size (~12 seconds per MB)
- Progress bars show transcription progress
- Existing transcripts are reused to save time and API costs
- Analysis results are always generated fresh, even for existing transcripts
- Real-time countdown timer shows transcription progress for individual files
- Progress bar shows overall progress when processing multiple files

## Error Handling

The tool handles several common errors:
- Missing API key
- File not found
- Invalid audio format
- API rate limits
- Failed transcriptions
- Failed analysis
- Invalid JSON responses

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
