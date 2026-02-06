## Odyssey World Model and OpenAI API Key to create videos

#### Works with Python 3.12 
#### Dependencies under pyproject.toml

### Setup
#### Clone repo
git clone git@github.com:ananyalahiri2003/odyssey-panchatantra.git

#### Create venv
python3.12 -m venv .venv
source .venv/bin/activate

#### Install ffmpeg
brew install ffmpeg

#### Install packages
python -m pip install -e ".[dev,ffmpeg]"

#### Create .env file for API keys, file should reside at project root and contain
ODYSSEY_API_KEY=ody_... # Fill in with your own API key
OPENAI_API_KEY=sk-... # As above

#### Run script from project root
python scripts/panchatantra_odyssey_with_tts.py

