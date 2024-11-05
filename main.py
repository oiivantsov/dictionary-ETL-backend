import os
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import psycopg2
from typing import List, Optional, Dict, Any

from wiktionaryparser import WiktionaryParser
from deep_translator import GoogleTranslator
from wiktionary_sanakirja_parser import WiktionaryParserFI

# Load .env only if not on Render
if not os.getenv("RENDER"):
    from dotenv import load_dotenv
    load_dotenv()

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

class WordData(BaseModel):
    date_added: Optional[str] = None
    date_repeated: Optional[str] = None
    level: Optional[int] = None
    word: str
    translation: Optional[str] = None
    category: Optional[str] = None
    category2: Optional[str] = None
    source: Optional[str] = None
    popularity: Optional[int] = None
    repeat_again: Optional[int] = None
    comment: Optional[str] = None
    example: Optional[str] = None
    synonyms: Optional[str] = None
    word_formation: Optional[str] = None
    frequency: Optional[int] = None

# Route to get all words
@app.get("/api/words", response_model=List[Dict])
async def get_all_words():
    query = "SELECT *, (CURRENT_DATE - date_repeated) AS days_since_last_repeat FROM finnish_dictionary"

    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    conn.close()

    return results

@app.get("/api/words/search")
async def search_words(word: Optional[str] = None, translation: Optional[str] = None):
    if not word and not translation:
        raise HTTPException(status_code=400, detail="Either 'word' or 'translation' must be provided.")

    # Constructing SQL query and parameters
    query = "SELECT *, (CURRENT_DATE - date_repeated) AS days_since_last_repeat FROM finnish_dictionary WHERE"
    params = []
    if word:
        query += " word ILIKE %s"
        params.append(f"%{word}%")
    elif translation:
        query += " translation ILIKE %s"
        params.append(f"%{translation}%")

    # Execute query and fetch results
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    conn.close()

    return results

@app.get("/api/words/stats")
async def get_words_statistics() -> Dict[str, Any]:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:

        # 1. Подсчет общего количества слов
        cursor.execute("SELECT COUNT(*) FROM finnish_dictionary")
        total_words = cursor.fetchone()["count"]

        # 2. Подсчет количества изученных слов (уровень >= 1)
        cursor.execute("SELECT COUNT(*) FROM finnish_dictionary WHERE level >= 1")
        studied_words = cursor.fetchone()["count"]

        # 3. Распределение по уровням и количеству дней с последнего повторения
        cursor.execute("""
            SELECT level, 
                   (CURRENT_DATE - date_repeated) AS days_since_last_repeat,
                   COUNT(*) AS count
            FROM finnish_dictionary
            WHERE date_repeated IS NOT NULL
            GROUP BY level, days_since_last_repeat
            ORDER BY level, days_since_last_repeat
        """)
        distribution_data = cursor.fetchall()

    # Обрабатываем полученные данные распределения
    distribution = {}
    all_days = set()
    for row in distribution_data:
        level = int(row["level"])
        days_since_last_repeat = int(row["days_since_last_repeat"])
        count = row["count"]

        # Структурируем данные по уровням и количеству дней
        if level not in distribution:
            distribution[level] = {}
        distribution[level][days_since_last_repeat] = count
        all_days.add(days_since_last_repeat)

    # Сортируем все уникальные дни для корректного отображения
    sorted_all_days = sorted(all_days)

    conn.close()

    # Возвращаем данные в структуре, которая нужна для фронтенда
    return {
        "totalWords": total_words,
        "studiedWords": studied_words,
        "allDays": sorted_all_days,
        "distribution": distribution
    }

@app.get("/api/words/is")
async def search_words(word: str):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM finnish_dictionary WHERE word = %s", (word,))
        results = cursor.fetchall()
    conn.close()

    return results

@app.post("/api/words")
async def add_word(word_data: WordData):
    print("Received data:", word_data.dict())
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO finnish_dictionary (
                date_added, date_repeated, level, word, translation, 
                category, category2, source, popularity, repeat_again, 
                comment, example, synonyms, word_formation, frequency
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            word_data.date_added, word_data.date_repeated, word_data.level, word_data.word,
            word_data.translation, word_data.category, word_data.category2, word_data.source,
            word_data.popularity, word_data.repeat_again, word_data.comment, word_data.example,
            word_data.synonyms, word_data.word_formation, word_data.frequency
        ))
        new_id = cursor.fetchone()[0]
        conn.commit()
    conn.close()

    return {"message": "Word added successfully", "id": new_id}

@app.put("/api/words/{word_id}")
async def update_word(word_id: int, word_data: WordData):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE finnish_dictionary
            SET date_added = %s, date_repeated = %s, level = %s, word = %s, 
                translation = %s, category = %s, category2 = %s, source = %s,
                popularity = %s, repeat_again = %s, comment = %s, example = %s, 
                synonyms = %s, word_formation = %s, frequency = %s
            WHERE id = %s
        """, (
            word_data.date_added, word_data.date_repeated, word_data.level, word_data.word,
            word_data.translation, word_data.category, word_data.category2, word_data.source,
            word_data.popularity, word_data.repeat_again, word_data.comment, word_data.example,
            word_data.synonyms, word_data.word_formation, word_data.frequency,
            word_id
        ))
        conn.commit()
    conn.close()

    return {"message": "Word updated successfully"}


@app.get("/api/words/filter")
async def filter_words(
        daysSinceLastRepeat: Optional[int] = Query(None),
        level: Optional[int] = Query(None),
        popularity: Optional[int] = Query(None),
        frequency: Optional[int] = Query(None),
        source: Optional[str] = Query(None),
        category1: Optional[str] = Query(None),
        category2: Optional[str] = Query(None),
        repeatAgain: Optional[int] = Query(None)
) -> List[Dict[str, Any]]:
    query = "SELECT * FROM finnish_dictionary WHERE TRUE"
    params = []

    # Добавляем фильтры в запрос при наличии значений
    if daysSinceLastRepeat is not None:
        query += " AND (CURRENT_DATE - date_repeated) = %s"
        params.append(daysSinceLastRepeat)
    if level is not None:
        query += " AND level = %s"
        params.append(level)
    if popularity is not None:
        query += " AND popularity = %s"
        params.append(popularity)
    if frequency is not None:
        query += " AND frequency = %s"
        params.append(frequency)
    if source:
        query += " AND source ILIKE %s"
        params.append(f"%{source}%")
    if category1:
        query += " AND category ILIKE %s"
        params.append(f"%{category1}%")
    if category2:
        query += " AND category2 ILIKE %s"
        params.append(f"%{category2}%")
    if repeatAgain is not None:
        query += " AND repeat_again = %s"
        params.append(repeatAgain)

    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    conn.close()

    return results


@app.put("/api/words/add-to-study/{word_id}")
async def add_word_to_study(word_id: int, date_repeated: str, level: int = 1):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE finnish_dictionary
            SET level = %s, date_repeated = %s
            WHERE id = %s
        """, (level, date_repeated, word_id))
        conn.commit()
    conn.close()

    return {"message": "Word added to study successfully"}

# Функция для парсинга данных с английской Wiki
def fetch_wiki_ENG(search_word: str) -> Dict[str, Any]:
    parser = WiktionaryParser()
    parser.set_default_language('Finnish')
    wiki_data = parser.fetch(search_word, 'Finnish')
    if not wiki_data or not wiki_data[0]:
        return {"error": "No data found"}

    etymology = wiki_data[0].get("etymology", "")
    definitions = wiki_data[0].get("definitions", [])

    if not definitions:
        return {"error": "No definitions found"}

    part_of_speech = definitions[0].get("partOfSpeech", "")
    all_definitions = definitions[0].get("text", [])[1:]

    examples_and_synonyms = definitions[0].get("examples", [])
    examples = [ex for ex in examples_and_synonyms if not ex.startswith("Synonyms")]
    synonyms = [syn.replace("Synonyms: ", "").replace("Synonym: ", "") for syn in examples_and_synonyms if
                syn.startswith("Synonyms") or syn.startswith("Synonym")]

    definitions_to_eng = ", ".join(all_definitions)
    definitions_to_rus = GoogleTranslator(source='en', target='ru').translate(definitions_to_eng)
    definitions_excel = f"{definitions_to_rus} \n{definitions_to_eng}"

    examples_excel = " // ".join(examples)
    synonyms_excel = ", ".join(synonyms)

    return {
        "definitions": definitions_excel,
        "PoS": part_of_speech,
        "examples": examples_excel,
        "synonyms": synonyms_excel,
        "etymology": etymology
    }


@app.get("/api/words/repeat")
async def get_words_for_repeat(level: int = Query(..., description="The level of words to repeat")):
    query = """
    SELECT *, (CURRENT_DATE - date_repeated) AS daysSinceLastRepeat 
    FROM finnish_dictionary 
    WHERE level = %s
      AND (CURRENT_DATE - date_repeated) = (
          SELECT MAX(CURRENT_DATE - date_repeated) 
          FROM finnish_dictionary 
          WHERE level = %s
      )
    """
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, (level, level))
        results = cursor.fetchall()
    conn.close()

    return results

@app.post("/api/words/upgrade")
async def upgrade_words_level(
        data: Dict[str, Any] = Body(...)
):
    level = data.get("level")
    days_since_last_repeat = data.get("daysSinceLastRepeat")
    date_repeated = data.get("date_repeated")

    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Обновляем слова, соответствующие уровню и количеству дней с последнего повторения
        cursor.execute("""
            UPDATE finnish_dictionary
            SET level = level + 1, date_repeated = %s
            WHERE level = %s AND (CURRENT_DATE - date_repeated) = %s
        """, (date_repeated, level, days_since_last_repeat))

        conn.commit()
    conn.close()

    return {"message": "Selected words have been upgraded to the next level"}


# Функция для парсинга данных с финской Wiki
def fetch_wiki_FI(search_word: str) -> Dict[str, Any]:
    parser_fi = WiktionaryParserFI()
    return parser_fi.fetch(search_word)

# Эндпоинт для парсинга данных с английской и финской Wiki
@app.get("/api/fetch-word")
async def fetch_word(word: str = Query(..., description="The word to search for in Wiktionary")):
    if not word:
        raise HTTPException(status_code=400, detail="Word is required")

    eng_data = fetch_wiki_ENG(word)
    fi_data = fetch_wiki_FI(word)

    return {
        "eng_data": eng_data,
        "fi_data": fi_data
    }