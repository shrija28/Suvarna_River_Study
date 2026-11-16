"""
Authentication & User Account Management Service
Estuarine Mouth Dynamics - Path Deviation Prediction System

Provides:
- SQLite user database with parameterized queries (prevents SQL injection).
- Secure password hashing using PBKDF2-HMAC-SHA256 (600,000 iterations + 32-byte salt).
- Constant-time timing-safe hash comparison (hmac.compare_digest).
- Account registration, credential authentication, and password reset.
- Remember-me credential caching.
"""

import os
import sqlite3
import hashlib
import hmac
import secrets
import json
from datetime import datetime
from typing import Optional, Dict, Tuple, Any


class AuthService:
    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            # Default database location inside data/ or qt_version/
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            data_dir = os.path.join(root_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "auth.db")
        else:
            self.db_path = db_path

        self.remember_file = os.path.join(os.path.dirname(self.db_path), ".remember_session.json")
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Initializes tables and seeds default administrative user accounts if database is fresh."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'Researcher',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active INTEGER NOT NULL DEFAULT 1
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                );
            """)

            # Check if any user exists
            cursor.execute("SELECT COUNT(*) AS cnt FROM users")
            row = cursor.fetchone()
            if row["cnt"] == 0:
                # Seed default researcher & admin accounts
                self._seed_user(cursor, "admin", "admin@suvarnariver.org", "admin123", "System Administrator", "Administrator")
                self._seed_user(cursor, "scientist", "scientist@suvarnariver.org", "scientist123", "Estuarine Geomorphologist", "Lead Researcher")
            conn.commit()

    def _seed_user(self, cursor: sqlite3.Cursor, username: str, email: str, password: str, full_name: str, role: str):
        salt = secrets.token_hex(16)
        pwd_hash = self._hash_password(password, salt)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, salt, algorithm, full_name, role, is_active)
            VALUES (?, ?, ?, ?, 'pbkdf2_sha256', ?, ?, 1)
        """, (username, email, pwd_hash, salt, full_name, role))

    @staticmethod
    def _hash_password(password: str, salt: str, iterations: int = 600_000) -> str:
        """Derives a secure cryptographic key using PBKDF2-HMAC-SHA256 (NIST/OWASP standard)."""
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations
        )
        return dk.hex()

    def authenticate(self, username_or_email: str, password: str, remember_me: bool = False) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Validates user credentials against the database.
        Returns: (user_dict, None) on success or (None, error_message) on failure.
        """
        u = (username_or_email or "").strip()
        p = (password or "").strip()

        if not u:
            return None, "Please enter your username or email address."
        if not p:
            return None, "Please enter your password."

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Parameterized query matching either username or email case-insensitively
                cursor.execute("""
                    SELECT id, username, email, password_hash, salt, algorithm, full_name, role, is_active
                    FROM users
                    WHERE username = ? OR email = ?
                """, (u, u))
                user = cursor.fetchone()

                if not user:
                    self._log_audit(conn, u, "LOGIN_ATTEMPT", "FAILED", "User not found")
                    return None, "Invalid username or password. Please verify your credentials."

                if not user["is_active"]:
                    self._log_audit(conn, u, "LOGIN_ATTEMPT", "BLOCKED", "Account deactivated")
                    return None, "This account has been deactivated. Please contact an administrator."

                salt = user["salt"]
                expected_hash = user["password_hash"]
                candidate_hash = self._hash_password(p, salt)

                # Timing-safe comparison to prevent side-channel timing attacks
                if not hmac.compare_digest(candidate_hash, expected_hash):
                    self._log_audit(conn, user["username"], "LOGIN_ATTEMPT", "FAILED", "Invalid password")
                    return None, "Invalid username or password. Please verify your credentials."

                # Update last login timestamp
                cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.utcnow().isoformat(), user["id"]))
                self._log_audit(conn, user["username"], "LOGIN_ATTEMPT", "SUCCESS", "Logged in successfully")
                conn.commit()

                user_dict = {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "role": user["role"],
                }

                if remember_me:
                    self.save_remembered_username(user["username"])
                else:
                    self.clear_remembered_username()

                return user_dict, None

        except sqlite3.Error as e:
            return None, f"Database error during authentication: {str(e)}"

    def register(self, username: str, email: str, password: str, confirm_password: str, full_name: str, role: str = "Researcher") -> Tuple[bool, Optional[str]]:
        """
        Registers a new user account with secure credentials.
        Returns: (True, None) on success or (False, error_message) on failure.
        """
        u = (username or "").strip()
        em = (email or "").strip().lower()
        fn = (full_name or "").strip()
        p = password or ""
        cp = confirm_password or ""

        if not u or not em or not p or not fn:
            return False, "All fields are required. Please fill in all information."

        if len(u) < 3:
            return False, "Username must be at least 3 characters long."

        if "@" not in em or "." not in em.split("@")[-1]:
            return False, "Please enter a valid email address (e.g., user@domain.com)."

        if len(p) < 6:
            return False, "Password must be at least 6 characters in length."

        if p != cp:
            return False, "Passwords do not match. Please re-enter both passwords."

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Check for existing username or email
                cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?", (u, em))
                existing = cursor.fetchone()
                if existing:
                    if existing["username"].lower() == u.lower():
                        return False, f"Username '{u}' is already taken. Please choose another."
                    else:
                        return False, f"Email '{em}' is already registered. Please sign in or use another."

                salt = secrets.token_hex(16)
                pwd_hash = self._hash_password(p, salt)

                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, salt, algorithm, full_name, role, is_active)
                    VALUES (?, ?, ?, ?, 'pbkdf2_sha256', ?, ?, 1)
                """, (u, em, pwd_hash, salt, fn, role))

                self._log_audit(conn, u, "USER_REGISTRATION", "SUCCESS", f"Account created for {fn} ({role})")
                conn.commit()
                return True, None

        except sqlite3.Error as e:
            return False, f"Database error during registration: {str(e)}"

    def reset_password(self, username_or_email: str, new_password: str, confirm_password: str) -> Tuple[bool, Optional[str]]:
        """Resets the password for an existing account."""
        u = (username_or_email or "").strip()
        p = new_password or ""
        cp = confirm_password or ""

        if not u:
            return False, "Please provide your username or email address."
        if not p or len(p) < 6:
            return False, "New password must be at least 6 characters in length."
        if p != cp:
            return False, "Passwords do not match. Please re-enter."

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username FROM users WHERE username = ? OR email = ?", (u, u))
                user = cursor.fetchone()
                if not user:
                    return False, "No registered account found with that username or email."

                salt = secrets.token_hex(16)
                pwd_hash = self._hash_password(p, salt)

                cursor.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (pwd_hash, salt, user["id"]))
                self._log_audit(conn, user["username"], "PASSWORD_RESET", "SUCCESS", "Password updated successfully")
                conn.commit()
                return True, None

        except sqlite3.Error as e:
            return False, f"Database error during password reset: {str(e)}"

    def _log_audit(self, conn: sqlite3.Connection, username: str, action: str, status: str, details: str = ""):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (username, action, status, details)
                VALUES (?, ?, ?, ?)
            """, (username, action, status, details))
        except Exception:
            pass

    def save_remembered_username(self, username: str):
        try:
            with open(self.remember_file, "w", encoding="utf-8") as f:
                json.dump({"username": username, "remember": True}, f)
        except Exception:
            pass

    def get_remembered_username(self) -> Optional[str]:
        try:
            if os.path.exists(self.remember_file):
                with open(self.remember_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("remember"):
                        return data.get("username")
        except Exception:
            pass
        return None

    def clear_remembered_username(self):
        try:
            if os.path.exists(self.remember_file):
                os.remove(self.remember_file)
        except Exception:
            pass


# Global singleton auth service instance
auth_service = AuthService()
