"""Firestore backend integration for LumenRise.

HARDCODED PROJECT ID: "qwiklabs-gcp-03-c47843160c69"
Do NOT change to google.auth.default() or GOOGLE_CLOUD_PROJECT because Agent Platform
injects the numerical project ID at runtime which breaks Firestore client initialization.
"""

from __future__ import annotations

import datetime
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-c47843160c69"

_db = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client bound to hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def get_affirmations(category: str = "general_mindfulness", limit: int = 5) -> str:
    """Reads curated daily affirmations from Firestore for a given category.

    Args:
        category: The affirmation category. Options: 'general_mindfulness',
          'literature_philosophy', 'sports_athletics', 'faith_spirituality', 'life_career'.
        limit: Maximum number of affirmations to fetch.

    Returns:
        A formatted string listing matching affirmations.
    """
    db = get_firestore_client()
    docs = (
        db.collection("affirmations")
        .where("category", "==", category)
        .limit(limit)
        .stream()
    )

    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(
            f"• Title: {data.get('title')}\n"
            f"  Content: \"{data.get('content')}\"\n"
            f"  Source: {data.get('author_source')}\n"
            f"  Theme: {data.get('theme')}"
        )

    if not results:
        all_docs = db.collection("affirmations").limit(limit).stream()
        for doc in all_docs:
            data = doc.to_dict()
            results.append(
                f"• Title: {data.get('title')}\n"
                f"  Content: \"{data.get('content')}\"\n"
                f"  Source: {data.get('author_source')}\n"
                f"  Theme: {data.get('theme')}"
            )

    if not results:
        return f"No affirmations found in database for category '{category}'."

    return f"Curated Affirmations ({category}):\n" + "\n\n".join(results)


def save_user_journal_entry(user_id: str, gratitude_text: str, intention: str, mood: str = "positive") -> str:
    """Saves a user's morning gratitude and intention entry to Firestore.

    Args:
        user_id: The unique user ID or alias.
        gratitude_text: What the user is grateful for today.
        intention: The user's goal or intention for the day.
        mood: The user's current morning mood/energy level.

    Returns:
        A confirmation message with the saved document ID.
    """
    db = get_firestore_client()
    entries_ref = db.collection("user_journal_entries")
    
    doc_data = {
        "user_id": user_id,
        "gratitude_text": gratitude_text,
        "intention": intention,
        "mood": mood,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    
    update_time, doc_ref = entries_ref.add(doc_data)
    return f"Successfully saved morning journal entry for user '{user_id}' with ID '{doc_ref.id}'."
