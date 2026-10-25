"""Shared pytest configuration for backend tests."""
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
