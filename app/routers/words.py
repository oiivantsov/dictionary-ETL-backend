from fastapi import APIRouter, Query, Body
from typing import List, Dict, Any, Optional
from app.config.database import get_db_connection
from app.models.word import WordData
from psycopg2.extras import RealDictCursor
from datetime import date, timedelta

router = APIRouter(prefix="/api/words")

@router.get("/", response_model=List[Dict])
async def get_all_words():
    query = "SELECT *, (CURRENT_DATE - date_repeated) AS days_since_last_repeat FROM finnish_dictionary"
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    conn.close()
    return results

@router.get("/search")
async def search_words(word: Optional[str] = None, translation: Optional[str] = None):
    if not word and not translation:
        raise HTTPException(status_code=400, detail="Either 'word' or 'translation' must be provided.")

    # Constructing SQL query and parameters
    query = "SELECT *, (CURRENT_DATE - date_repeated) AS days_since_last_repeat FROM finnish_dictionary WHERE"
    params = []
    if word:
        query += " LOWER(word) ILIKE %s"
        params.append(f"%{word}%")
    elif translation:
        query += " LOWER(translation) ILIKE %s"
        params.append(f"%{translation}%")

    # Execute query and fetch results
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    conn.close()

    return results

@router.get("/stats")
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

@router.get("/is")
async def search_words(word: str):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM finnish_dictionary WHERE word = %s", (word,))
        results = cursor.fetchall()
    conn.close()

    return results

from fastapi import HTTPException

@router.post("/")
async def add_word(word_data: WordData):
    print("Received data:", word_data.dict())
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Check if the word already exists in the database
        cursor.execute("SELECT id FROM finnish_dictionary WHERE word = %s", (word_data.word,))
        existing_word = cursor.fetchone()

        if existing_word:
            # Word already exists, return a message without adding
            conn.close()
            raise HTTPException(status_code=409, detail="Word already exists in the dictionary")

        # Insert the word if it doesn't exist
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

@router.put("/{word_id}")
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


@router.get("/filter")
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


@router.get("/repeat")
async def get_words_for_repeat(
        level: int = Query(..., description="The level of words to repeat"),
        days_since_last_repeat: int = Query(None, description="Optional filter for days since last repeat")
):
    conn = get_db_connection()

    if days_since_last_repeat is not None:
        # Calculate the target date based on the provided number of days
        target_date = date.today() - timedelta(days=days_since_last_repeat)
        query = """
        SELECT *, CURRENT_DATE - date_repeated AS daysSinceLastRepeat
        FROM finnish_dictionary
        WHERE level = %s
          AND date_repeated = %s
        """
        params = [level, target_date]
    else:
        # Use a CTE to find the maximum date_repeated and filter words
        query = """
        WITH min_date_cte AS (
            SELECT MIN(date_repeated) AS min_date
            FROM finnish_dictionary
            WHERE level = %s
        )
        SELECT *, CURRENT_DATE - date_repeated AS daysSinceLastRepeat
        FROM finnish_dictionary
        WHERE level = %s
          AND date_repeated = (SELECT min_date FROM min_date_cte)
        """
        params = [level, level]

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
    conn.close()

    return results

@router.get("/level-days")
async def get_level_days():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT level, MAX(CURRENT_DATE - date_repeated) AS daysSinceLastRepeat
            FROM finnish_dictionary
            GROUP BY level
            having level between 1 and 12
            order by level
        """)
        results = cursor.fetchall()
    conn.close()

    return results

@router.post("/upgrade")
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


@router.post("/bulk-update-level")
async def bulk_update_level(
    data: Dict[str, Any] = Body(...)
):

    ids = data.get("ids")
    level = data.get("level")
    date_repeated = data.get("date_repeated")

    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Construct a single query with WHERE id IN (...)
        cursor.execute(f"""
            UPDATE finnish_dictionary
            SET level = %s, date_repeated = %s
            WHERE id = ANY(%s::int[])
        """, (level, date_repeated, ids))
        conn.commit()
    conn.close()

    return {"message": "Selected words updated successfully"}


@router.delete("/{word_id}")
async def delete_word(word_id: int):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Check if the word exists
        cursor.execute("SELECT id FROM finnish_dictionary WHERE id = %s", (word_id,))
        word = cursor.fetchone()

        if not word:
            conn.close()
            raise HTTPException(status_code=404, detail="Word not found")

        # Delete the word
        cursor.execute("DELETE FROM finnish_dictionary WHERE id = %s", (word_id,))
        conn.commit()
    conn.close()

    return {"message": "Word deleted successfully"}
