from fastapi import APIRouter, Query, HTTPException
from app.utils.web_parser import fetch_wiki_ENG, fetch_wiki_FI, fetch_slang

router = APIRouter(prefix="/api")

@router.get("/fetch-word-eng")
async def fetch_word_eng(word: str = Query(..., description="The word to search for in English Wiktionary")):
    if not word:
        raise HTTPException(status_code=400, detail="Word is required")
    eng_data = fetch_wiki_ENG(word)
    return {"eng_data": eng_data}

@router.get("/fetch-word-fi")
async def fetch_word_fi(word: str = Query(..., description="The word to search for in Finnish Wiktionary")):
    if not word:
        raise HTTPException(status_code=400, detail="Word is required")
    fi_data = fetch_wiki_FI(word)
    return {"fi_data": fi_data}

@router.get("/fetch-word-slang")
async def fetch_word_slang(word: str = Query(..., description="The word to search for")):
    if not word:
        raise HTTPException(status_code=400, detail="Word is required")
    custom_data = fetch_slang(word)
    return {"slang_data": custom_data}
