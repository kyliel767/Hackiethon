 ## Description of the game
 "Wolf's Canon Rewrite" is an adventure game in which you as the player is
 hit by a truck and transported to the world of Little Red Riding Hood. You awaken as the Big Bad Wolf, and a mysterious entity tells you that you must change
 the original plot and avert your death, in order to be
 transported back to your world. You encounter a creature throughout your
 journey that will guide you towards Little Red Riding Hood. Good luck!

 ## How AI was integrated
 We used the Groq API model LLama-3.3-70b for the dialogue of the NPCs
 of the game, such as for Gnome and Little Red Riding Hood. Their dialogue
 was based on the player's input which allowed the model to make decisions that determined the ending of the game.


## How to run the game
### Getting a Groq API Key
1. Head to https://console.groq.com/keys
2. Create an account
3. Select "Create API Key" and give your API key a name and create
4. Make sure ytou copy the key as it will not be displayed again
5. Create a new .env file in the project folder and type in the following:
`GROQ_API_KEY = "[API_KEY]"`, replacing `[API_KEY]` with your API key you copied

### Installing packages to run the API 
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
## Technologies used
* Pygame

## Acknowledgments
We thank HackMelbourne for running the 2026 Hackiethon, providing 
food and providing help. We acknowledge the creators of the assets
we have used in this game for their creative designs and music.

