"""
Module frontend: Defines all routes that are part of this applications frontend.
All routes in here return a server-side rendered HTML page.
"""
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.redis_service import get_state, set_state

from app.services.pokemon_service import fetch_pokemon
from app.util.logger import get_logger

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
logger = get_logger("Frontend")

# In-memory session store (basic)
sessions = {}


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home site.

    Args:
        request (Request): request body

    Returns:
        TemplateResponse: Returns the HTML Template to be displayed in the clients browser.
    """
    logger.info(msg="Accessing home page.")
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Route for the login-frontend

    Args:
        request (Request): request body

    Returns:
        TemplateResponse: HTML to be displayed in the browser
    """
    logger.info(msg="Accessing login page.")
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """Register Route. Provides the frontend to give users the opportunity to sell their
       soul to this website.

    Args:
        request (Request): Request

    Returns:
        TemplateResponse: The HTML Template to be displayed
    """
    logger.info(msg="Accessing registration page.")
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/highscores", response_class=HTMLResponse)
async def highscore_page(request: Request):
    """Highscores Page. Can only be accessed if the user is logged in.
       That is handled in the js code however.

    Args:
        request (Request): reqeust body

    Returns:
        HTMLResponse: Highscores Page to be displayed in the browser.
    """
    logger.info(msg="Accessing highscores page.")
    return templates.TemplateResponse("highscores.html", {
        "request": request
    })


@router.get("/quiz", response_class=HTMLResponse)
async def get_quiz(request: Request):
    """Quiz page. Uses templating cimbined with a fetch from the redis container (where
    the quiz data is stored at) to return a server-side rendered thing

    Args:
        request (Request): reqeust body

    Returns:
        HTMLResponse: Quiz Page (rendered).
    """
    logger.info("Accessing quiz page.")

    session_id = request.cookies.get("quiz_session_id")

    if session_id is None:
        logger.warning(
            "Missing quiz_session_id cookie in /quiz. Redirecting to /api/start_quiz")
        return RedirectResponse(url="/api/start_quiz")

    state = get_state(session_id)
    if not state:
        pokemon = fetch_pokemon(logger)
        set_state(session_id, pokemon.__dict__)
        state = pokemon.__dict__

    logger.info(f"Pokemon information captured: {state}")
    return templates.TemplateResponse(
        "quiz.html",
        {
            "request": request,
            "message": "",
            "reload": False,
            "pokemon": state,
        }
    )
