import datetime
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-c47843160c69"

def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    affirmations_ref = db.collection("affirmations")

    sample_items = [
        {
            "id": "gen_01",
            "category": "general_mindfulness",
            "title": "A Fresh Beginning",
            "content": "Today is a new canvas. Embrace the quiet morning calm and step forward with confidence.",
            "author_source": "Universal Mindfulness",
            "theme": "Peace & Gratitude",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "lit_01",
            "category": "literature_philosophy",
            "title": "Morning Citadel",
            "content": "When you arise in the morning think of what a privilege it is to be alive, to think, to enjoy, to love.",
            "author_source": "Marcus Aurelius (Meditations)",
            "theme": "Stoic Wisdom",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "sports_01",
            "category": "sports_athletics",
            "title": "Daily Discipline",
            "content": "Champions aren't made in gyms. Champions are made from something they have deep inside them—a desire, a dream, a vision.",
            "author_source": "Muhammad Ali",
            "theme": "Grit & Perseverance",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "faith_01",
            "category": "faith_spirituality",
            "title": "Light and Strength",
            "content": "Faith is taking the first step even when you don't see the whole staircase.",
            "author_source": "Dr. Martin Luther King Jr.",
            "theme": "Faith & Reflection",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "career_01",
            "category": "life_career",
            "title": "Purposeful Action",
            "content": "Far and away the best prize that life has to offer is the chance to work hard at work worth doing.",
            "author_source": "Theodore Roosevelt",
            "theme": "Career & Life Transitions",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
    ]

    for item in sample_items:
        doc_ref = affirmations_ref.document(item["id"])
        doc_ref.set(item)
        print(f"Seeded document: {item['id']} ({item['category']})")

    print("\nFirestore seeding complete!")

if __name__ == "__main__":
    seed_database()
