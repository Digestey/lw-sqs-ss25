# app/routes/frontend.py

from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from services.auth_service import get_user_from_token, oauth2_scheme

from services.pokemon_service import fetch_pokemon
from util.logger import get_logger

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = get_logger("Frontend")

# In-memory session store (basic)
sessions = {}


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/highscores", response_class=HTMLResponse)
async def highscore_page(request: Request):
    return templates.TemplateResponse("highscores.html", {
        "request": request
    })

@router.get("/quiz", response_class=HTMLResponse)
async def get_quiz(request: Request):
    session_id = request.client.host
    if session_id not in sessions:
        sessions[session_id] = fetch_pokemon(logger)

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


@router.post("/quiz", response_class=JSONResponse)
async def post_quiz(request: Request, guess: str = Form(...)):
    session_id = request.client.host
    if session_id not in sessions:
        sessions[session_id] = fetch_pokemon(logger)

    pokemon_info = sessions[session_id]
    correct_answer = pokemon_info.name.lower()
    guess = guess.strip().lower()

    if guess == correct_answer:
        del sessions[session_id]
        return JSONResponse(content={"correct": True, "message": "Ding Ding Ding! We have a winner!"})

    return JSONResponse(content={
        "correct": False,
        "message": "That is incorrect. Another hint has been added to the entry.",
        "hint": ""  # Later you could add stats/types one by one
    })
