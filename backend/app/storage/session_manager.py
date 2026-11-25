"""Session and storage management for isolated dataset operations."""
import json
import os
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from app.core.config import settings
from app.core.exceptions import AppException, SessionNotFoundError, ValidationError

_SESSION_LOCKS: dict[str, Lock] = {}
_GLOBAL_LOCK = Lock()


def _get_session_lock(session_id: str) -> Lock:
    """Thread-safe acquisition of a per-session lock."""
    with _GLOBAL_LOCK:
        if session_id not in _SESSION_LOCKS:
            _SESSION_LOCKS[session_id] = Lock()
        return _SESSION_LOCKS[session_id]


class SessionManager:
    """Manages ephemeral session directories, file I/O, and lifecycle janitor."""

    @staticmethod
    def validate_session_id(session_id: str) -> str:
        """Strictly validate that the session ID is a valid UUIDv4 string.
        
        Prevents path traversal attacks and malformed identifiers.
        """
        if not session_id or not isinstance(session_id, str):
            raise ValidationError("Session ID must be a non-empty string.")
        try:
            val = uuid.UUID(session_id, version=4)
            if str(val) != session_id.lower():
                raise ValueError()
        except (ValueError, AttributeError):
            raise ValidationError(f"Invalid session ID format '{session_id}'. Must be a valid UUIDv4.")
        return session_id.lower()

    @classmethod
    def get_session_dir(cls, session_id: str, create: bool = False) -> Path:
        """Return the absolute path to a session's directory."""
        valid_id = cls.validate_session_id(session_id)
        session_path = settings.storage_path / valid_id
        if create:
            session_path.mkdir(parents=True, exist_ok=True)
        return session_path

    @classmethod
    def create_session(cls) -> str:
        """Create a new unique session directory and return its UUID."""
        session_id = str(uuid.uuid4())
        session_dir = cls.get_session_dir(session_id, create=True)
        # Touch metadata
        now_iso = datetime.now(timezone.utc).isoformat()
        initial_meta = {
            "session_id": session_id,
            "created_at": now_iso,
            "last_accessed": now_iso,
            "status": "initialized"
        }
        with open(session_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(initial_meta, f, indent=2)
        return session_id

    @classmethod
    def session_exists(cls, session_id: str) -> bool:
        """Check if an active session directory exists."""
        try:
            valid_id = cls.validate_session_id(session_id)
            session_dir = settings.storage_path / valid_id
            return session_dir.is_dir() and (session_dir / "metadata.json").is_file()
        except ValidationError:
            return False

    @classmethod
    def touch_session(cls, session_id: str) -> None:
        """Update the last accessed timestamp for a session."""
        session_dir = cls.get_session_dir(session_id)
        meta_file = session_dir / "metadata.json"
        if not meta_file.is_file():
            raise SessionNotFoundError(session_id)
        
        lock = _get_session_lock(session_id)
        with lock:
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["last_accessed"] = datetime.now(timezone.utc).isoformat()
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

    @classmethod
    def save_raw_dataset(
        cls,
        session_id: str,
        df: pd.DataFrame,
        metadata_dict: dict,
        original_bytes: bytes | None = None,
        original_filename: str | None = None
    ) -> None:
        """Save raw immutable dataframe as Parquet and write metadata.
        
        Optionally preserves original binary upload for Excel multi-sheet access.
        """
        session_dir = cls.get_session_dir(session_id, create=True)
        lock = _get_session_lock(session_id)

        with lock:
            # 1. Save raw immutable Parquet
            parquet_path = session_dir / "raw.parquet"
            # Ensure column names are strings for PyArrow compatibility
            clean_df = df.copy()
            clean_df.columns = [str(c) for c in clean_df.columns]
            table = pa.Table.from_pandas(clean_df, preserve_index=False)
            pq.write_table(table, parquet_path, compression="snappy")

            # 2. Optionally store original file for sheet switching or audit
            if original_bytes and original_filename:
                ext = Path(original_filename).suffix.lower()
                orig_path = session_dir / f"original{ext}"
                with open(orig_path, "wb") as f:
                    f.write(original_bytes)
                metadata_dict["original_file"] = str(orig_path.name)

            # 3. Update metadata
            metadata_dict["session_id"] = session_id
            now_iso = datetime.now(timezone.utc).isoformat()
            metadata_dict["created_at"] = metadata_dict.get("created_at", now_iso)
            metadata_dict["last_accessed"] = now_iso

            with open(session_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata_dict, f, indent=2)

    @classmethod
    def get_raw_dataset(cls, session_id: str) -> pd.DataFrame:
        """Load and return the immutable raw dataset as a Pandas DataFrame."""
        if not cls.session_exists(session_id):
            raise SessionNotFoundError(session_id)
        
        session_dir = cls.get_session_dir(session_id)
        parquet_path = session_dir / "raw.parquet"
        if not parquet_path.is_file():
            raise SessionNotFoundError(session_id)

        cls.touch_session(session_id)
        table = pq.read_table(parquet_path)
        return table.to_pandas()

    @classmethod
    def get_metadata(cls, session_id: str) -> dict:
        """Read and return current session metadata."""
        if not cls.session_exists(session_id):
            raise SessionNotFoundError(session_id)
        
        session_dir = cls.get_session_dir(session_id)
        meta_file = session_dir / "metadata.json"
        
        lock = _get_session_lock(session_id)
        with lock:
            with open(meta_file, "r", encoding="utf-8") as f:
                return json.load(f)

    @classmethod
    def update_metadata(cls, session_id: str, updates: dict) -> dict:
        """Update existing session metadata with key-value pairs."""
        if not cls.session_exists(session_id):
            raise SessionNotFoundError(session_id)
        
        session_dir = cls.get_session_dir(session_id)
        meta_file = session_dir / "metadata.json"
        
        lock = _get_session_lock(session_id)
        with lock:
            with open(meta_file, "r", encoding="utf-8") as f:
                current = json.load(f)
            current.update(updates)
            current["last_accessed"] = datetime.now(timezone.utc).isoformat()
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2)
            return current

    @classmethod
    def get_original_file_path(cls, session_id: str) -> Path | None:
        """Return the path to the original raw uploaded file if preserved."""
        meta = cls.get_metadata(session_id)
        orig_file = meta.get("original_file")
        if orig_file:
            path = cls.get_session_dir(session_id) / orig_file
            if path.is_file():
                return path
        return None

    @classmethod
    def cleanup_expired_sessions(cls) -> int:
        """Scan storage directory and delete sessions inactive for > SESSION_EXPIRY_HOURS.
        
        Returns the number of purged sessions.
        """
        now = time.time()
        expiry_seconds = settings.SESSION_EXPIRY_HOURS * 3600
        purged = 0

        storage_root = settings.storage_path
        if not storage_root.exists():
            return 0

        for entry in storage_root.iterdir():
            if entry.is_dir():
                meta_file = entry / "metadata.json"
                should_delete = False
                if meta_file.is_file():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        last_acc_str = data.get("last_accessed")
                        if last_acc_str:
                            last_acc_dt = datetime.fromisoformat(last_acc_str)
                            # Convert to timestamp
                            age = now - last_acc_dt.timestamp()
                            if age > expiry_seconds:
                                should_delete = True
                        else:
                            # Fallback to directory mtime
                            if (now - entry.stat().st_mtime) > expiry_seconds:
                                should_delete = True
                    except Exception:
                        should_delete = True
                else:
                    # Stale or malformed directory
                    if (now - entry.stat().st_mtime) > expiry_seconds:
                        should_delete = True

                if should_delete:
                    try:
                        shutil.rmtree(entry)
                        purged += 1
                        with _GLOBAL_LOCK:
                            _SESSION_LOCKS.pop(entry.name, None)
                    except Exception:
                        pass

        return purged

