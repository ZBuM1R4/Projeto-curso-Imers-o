import json
import sqlite3
from pathlib import Path


DB_PATH = Path("data/database.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        video_name TEXT,
        score INTEGER,
        transcription TEXT,
        report_json TEXT,
        ai_available INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("PRAGMA table_info(analyses)")
    columns = [column[1] for column in cursor.fetchall()]

    if "ai_available" not in columns:
        cursor.execute("""
        ALTER TABLE analyses
        ADD COLUMN ai_available INTEGER DEFAULT 1
        """)

    conn.commit()
    conn.close()


def save_analysis(report: dict, video_path: str):
    conn = get_connection()
    cursor = conn.cursor()

    title = Path(video_path).stem
    score = report["score_comunicacao"]["score"]
    transcription = report["transcricao"]

    ai_available = 1 if report.get("analise_global_ia", {}).get("disponivel") else 0

    cursor.execute("""
    DELETE FROM analyses
    WHERE video_name = ?
    """, (video_path,))

    cursor.execute("""
    INSERT INTO analyses (
        title,
        video_name,
        score,
        transcription,
        report_json,
        ai_available
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        video_path,
        score,
        transcription,
        json.dumps(report, ensure_ascii=False),
        ai_available
    ))

    conn.commit()
    conn.close()


def get_all_analyses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title, score, created_at, ai_available
    FROM analyses
    ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_analysis_by_id(analysis_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT report_json
    FROM analyses
    WHERE id = ?
    """, (analysis_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return json.loads(row[0])


def delete_analysis(analysis_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM analyses
    WHERE id = ?
    """, (analysis_id,))

    conn.commit()
    conn.close()


def get_average_score():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT AVG(score)
    FROM analyses
    """)

    result = cursor.fetchone()[0]
    conn.close()

    return round(result, 2) if result else 0


def get_score_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT title, score, created_at
    FROM analyses
    ORDER BY created_at ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_history_stats():
    history = get_score_history()

    if not history:
        return {
            "total_analyses": 0,
            "best_score": 0,
            "score_delta": 0,
        }

    scores = [row[1] for row in history]

    return {
        "total_analyses": len(scores),
        "best_score": max(scores),
        "score_delta": scores[-1] - scores[0],
    }