"""
==========================================================
AI JobAgent - Discovered Job Repository
Unified repository for managing ATS-discovered jobs in SQLite.
Prevents duplicate entries via UNIQUE(provider, company_key, external_job_id).
==========================================================
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parents[1]


def get_default_db_path() -> Path:
    """Resolve active SQLite database path with fallback."""
    data_db = ROOT_DIR / "data" / "job_copilot.db"
    if data_db.parent.exists():
        return data_db
    root_db = ROOT_DIR / "job_copilot.db"
    return root_db


def initialize_jobs_table(db_path: Optional[Union[str, Path]] = None) -> None:
    """
    Ensure the discovered_jobs table exists in SQLite.
    Stores unified vacancies across all ATS platforms (Greenhouse, Lever, Ashby, etc.).
    """
    path = Path(db_path) if db_path else get_default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(str(path)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS discovered_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                provider TEXT NOT NULL,
                company_key TEXT NOT NULL,
                external_job_id TEXT NOT NULL,
                job_title TEXT NOT NULL,
                location TEXT,
                official_job_url TEXT NOT NULL,
                apply_url TEXT,
                description TEXT,
                posted_at TEXT,
                url_verified INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'open',
                first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (
                    provider,
                    company_key,
                    external_job_id
                )
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_discovered_jobs_provider
            ON discovered_jobs (provider, company_key)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_discovered_jobs_status
            ON discovered_jobs (status)
        """)
        conn.commit()


def save_job(conn: sqlite3.Connection, job: Dict[str, Any]) -> bool:
    """
    Save or update a discovered ATS vacancy.
    Prevents repeated synchronizations from creating duplicates.
    Inserts new records and updates existing ones on conflict.
    """
    if not job or not job.get("official_job_url"):
        return False

    provider = str(job.get("provider") or "generic").lower().strip()
    company_key = str(job.get("company_key") or "").strip()
    external_job_id = str(job.get("external_job_id") or job.get("job_id") or "").strip()

    if not external_job_id:
        return False

    company_name = str(job.get("company_name") or job.get("company") or "Company").strip()
    job_title = str(job.get("job_title") or job.get("title") or "Role").strip()
    location = str(job.get("location") or "Remote").strip()
    official_job_url = str(job.get("official_job_url") or job.get("job_url") or "").strip()
    apply_url = str(job.get("apply_url") or official_job_url).strip()
    description = str(job.get("description") or "").strip()
    posted_at = str(job.get("posted_at") or "").strip()
    url_verified = 1 if job.get("url_verified") else 0
    status = str(job.get("status") or "open").lower().strip()

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO discovered_jobs (
            company_name,
            provider,
            company_key,
            external_job_id,
            job_title,
            location,
            official_job_url,
            apply_url,
            description,
            posted_at,
            url_verified,
            status,
            last_seen_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(provider, company_key, external_job_id) DO UPDATE SET
            company_name = excluded.company_name,
            job_title = excluded.job_title,
            location = excluded.location,
            official_job_url = excluded.official_job_url,
            apply_url = excluded.apply_url,
            description = excluded.description,
            posted_at = excluded.posted_at,
            status = 'open',
            last_seen_at = CURRENT_TIMESTAMP
    """, (
        company_name,
        provider,
        company_key,
        external_job_id,
        job_title,
        location,
        official_job_url,
        apply_url,
        description,
        posted_at,
        url_verified,
        status,
    ))
    return True


def get_discovered_jobs(
    conn_or_path: Optional[Union[sqlite3.Connection, str, Path]] = None,
    limit: int = 100,
    verified_only: bool = False,
    search: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    status: str = "open"
) -> List[Dict[str, Any]]:
    """
    Retrieve discovered jobs from the repository with optional filtering.
    Returns normalized dictionary objects compatible with Flask templates.
    """
    should_close = False
    if isinstance(conn_or_path, sqlite3.Connection):
        conn = conn_or_path
    else:
        path = Path(conn_or_path) if conn_or_path else get_default_db_path()
        if not path.exists():
            return []
        conn = sqlite3.connect(str(path))
        should_close = True

    conn.row_factory = sqlite3.Row
    try:
        query = "SELECT * FROM discovered_jobs WHERE 1=1"
        params: List[Any] = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if verified_only:
            query += " AND url_verified = 1"

        if search:
            query += " AND (job_title LIKE ? OR company_name LIKE ? OR description LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        if role:
            query += " AND job_title LIKE ?"
            params.append(f"%{role}%")

        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")

        query += " ORDER BY last_seen_at DESC LIMIT ?"
        params.append(limit)

        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "id": f"disc_{row['id']}",
                "db_id": row["id"],
                "company_name": row["company_name"],
                "company": row["company_name"],
                "provider": row["provider"],
                "ats_provider": row["provider"].capitalize(),
                "company_key": row["company_key"],
                "external_job_id": row["external_job_id"],
                "job_id": row["external_job_id"],
                "job_title": row["job_title"],
                "title": row["job_title"],
                "location": row["location"] or "Remote",
                "official_job_url": row["official_job_url"],
                "apply_url": row["apply_url"] or row["official_job_url"],
                "url": row["apply_url"] or row["official_job_url"],
                "description": row["description"] or "",
                "posted_at": row["posted_at"] or "",
                "posted_date": "Active Live (Today)",
                "url_verified": bool(row["url_verified"]),
                "status": row["status"],
                "is_live": True,
            })
        return results
    finally:
        if should_close:
            conn.close()


def get_discovered_job_by_id(
    job_id: Union[str, int],
    conn_or_path: Optional[Union[sqlite3.Connection, str, Path]] = None
) -> Optional[Dict[str, Any]]:
    """Retrieve a single discovered job by numeric id or external_job_id."""
    clean_id = str(job_id).replace("disc_", "")
    should_close = False
    if isinstance(conn_or_path, sqlite3.Connection):
        conn = conn_or_path
    else:
        path = Path(conn_or_path) if conn_or_path else get_default_db_path()
        if not path.exists():
            return None
        conn = sqlite3.connect(str(path))
        should_close = True

    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM discovered_jobs
            WHERE id = ? OR external_job_id = ?
            LIMIT 1
        """, (clean_id, str(job_id)))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": f"disc_{row['id']}",
            "db_id": row["id"],
            "company_name": row["company_name"],
            "company": row["company_name"],
            "provider": row["provider"],
            "ats_provider": row["provider"].capitalize(),
            "company_key": row["company_key"],
            "external_job_id": row["external_job_id"],
            "job_id": row["external_job_id"],
            "job_title": row["job_title"],
            "title": row["job_title"],
            "location": row["location"] or "Remote",
            "official_job_url": row["official_job_url"],
            "apply_url": row["apply_url"] or row["official_job_url"],
            "url": row["apply_url"] or row["official_job_url"],
            "description": row["description"] or "",
            "posted_at": row["posted_at"] or "",
            "posted_date": "Active Live (Today)",
            "url_verified": bool(row["url_verified"]),
            "status": row["status"],
            "is_live": True,
        }
    finally:
        if should_close:
            conn.close()


def mark_job_verified(
    job_id: Union[str, int],
    verified: bool = True,
    conn_or_path: Optional[Union[sqlite3.Connection, str, Path]] = None
) -> bool:
    """Update url_verified status in the repository."""
    clean_id = str(job_id).replace("disc_", "")
    should_close = False
    if isinstance(conn_or_path, sqlite3.Connection):
        conn = conn_or_path
    else:
        path = Path(conn_or_path) if conn_or_path else get_default_db_path()
        conn = sqlite3.connect(str(path))
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE discovered_jobs
            SET url_verified = ?, last_seen_at = CURRENT_TIMESTAMP
            WHERE id = ? OR external_job_id = ?
        """, (1 if verified else 0, clean_id, str(job_id)))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        if should_close:
            conn.close()


def mark_job_closed(
    provider: str,
    company_key: str,
    external_job_id: str,
    conn_or_path: Optional[Union[sqlite3.Connection, str, Path]] = None
) -> bool:
    """Mark a confirmed closed vacancy."""
    should_close = False
    if isinstance(conn_or_path, sqlite3.Connection):
        conn = conn_or_path
    else:
        path = Path(conn_or_path) if conn_or_path else get_default_db_path()
        conn = sqlite3.connect(str(path))
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE discovered_jobs
            SET status = 'closed', last_seen_at = CURRENT_TIMESTAMP
            WHERE provider = ? AND company_key = ? AND external_job_id = ?
        """, (provider.lower().strip(), company_key.strip(), str(external_job_id).strip()))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        if should_close:
            conn.close()
