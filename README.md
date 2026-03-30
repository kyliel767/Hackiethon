# How to run the game
## Getting a Groq API Key
1. Head to https://console.groq.com/keys
2. Create an account
3. Select "Create API Key" and give your API key a name and create
4. Make sure ytou copy the key as it will not be displayed again
5. Create a new .env file in the project folder and type in the following:
GROQ_API_KEY = "[API_KEY]", replacing [API_KEY] with your API key you copied

## Installing packages to run the API 
1. Start by creating a virtual environment 
On MACOS:
```bash
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```
On Windows:
```bash
py -m venv .venv

.venv\scripts\activate.bat

pip install -r requirements.txt
```
