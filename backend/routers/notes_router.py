from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import json
import os

router = APIRouter(prefix="/notes", tags=["Notes"])

DATA_PATH = os.path.join("backend", "data", "notes.json")

class Note(BaseModel):
    user_id: str
    movie_id: str
    content: Optional[str] = ""

# Read JSON file
def load_notes():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)

# Write JSON file
def save_notes(notes):
    with open(DATA_PATH, "w") as f:
        json.dump(notes, f, indent=4)

@router.get("/{user_id}/{movie_id}")
def get_note(user_id: str, movie_id: str):
    notes = load_notes()
    for n in notes:
        if n["user_id"] == user_id and n["movie_id"] == movie_id:
            return n
    return {"content": ""}

@router.post("/")
def save_note(note: Note):
    notes = load_notes()

    # Find if it already exists -> update
    for n in notes:
        if n["user_id"] == note.user_id and n["movie_id"] == note.movie_id:
            n["content"] = note.content
            save_notes(notes)
            return {"message": "Note updated"}

    # Otherwise add new
    notes.append(note.dict())
    save_notes(notes)
    return {"message": "Note added"}
