# app.py
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
import pokebase as pb
from dotenv import load_dotenv
from pokemon_api import fetch_pokemon

# Initialization of the application

load_dotenv()

sessions = {}
app = FastAPI()
templates = Jinja2Templates(directory="templates")

pb.cache.set_cache(os.getenv("POKEMON_CACHE"))

# print(f"{dir(pb.cache.API_CACHE)}")

# Mount the required directories for the webpage

app.mount(
    "/static",
    StaticFiles(directory=Path("static/")),
    name="static",
)
app.mount(
    "/images",
    StaticFiles(directory=Path("images/")),
    name="images"
)



# Route for the homepage


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Load home template
    return templates.TemplateResponse("index.html", {"request": request, "user_name": "John Doe"})


@app.post("/submit", response_class=HTMLResponse)
async def submit(request: Request, name: str = Form(...)):
    return templates.TemplateResponse("index.html", {"request": request, "user_name": name})


@app.get("/quiz")
async def get_quiz(request: Request):
    session_id = request.client.host  # Use client IP as a simple session identifier
    if session_id not in sessions:
        sessions[session_id] = fetch_pokemon()

    pokemon_info = sessions[session_id]

    return templates.TemplateResponse(
        "quiz.html",
        {
            "request": request,
            "message": "",
            "reload": False,
            "pokemon": pokemon_info
        }
    )


@app.post("/quiz")
async def post_quiz(request: Request, guess: str = Form(...)):
    session_id = request.client.host
    if session_id not in sessions:
        sessions[session_id] = fetch_pokemon()

    correct_answer = sessions[session_id]["name"].lower()
    guess = guess.strip().lower()

    if guess == correct_answer:
        del sessions[session_id]  # Reset session on correct guess
        return JSONResponse(content={"correct": True, "message": "Ding Ding Ding! We have a winner!"})

    return JSONResponse(content={"correct": False, "message": "That is incorrect. Another hint has been added to the entry", "hint": ""})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
