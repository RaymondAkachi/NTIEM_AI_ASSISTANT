# config.py
PRAYER_SUPPORT = {
    "categories": {
        "marriage": {
            "response": "Contact marriage prayer team: 555-1234",
            "keywords": ["marriage", "spouse", "wedding", "divorce"],
            "scripture": "Matthew 19:6 - 'What God has joined together...'",
            "auto_prayer": "Lord, we pray for strength and wisdom in this marriage..."
        },
        "health": {
            "response": "Health prayer line: 555-5678",
            "keywords": ["healing", "sickness", "recovery", "diagnosis"],
            "scripture": "Jeremiah 30:17 - 'I will restore health to you...'",
            "auto_prayer": "Heavenly Father, we ask for Your healing touch..."
        },
        "default": {
            "response": "General prayer: 555-0000",
            "scripture": "Philippians 4:6 - 'Do not be anxious about anything...'",
            "auto_prayer": "Lord, we lift up this need to You..."
        }
    },
    "escalation_paths": {
        "crisis": "24/7 Crisis Prayer Line: 555-9999",
        "follow_up": "Would you like us to share this request with your local church?"
    }
}

# config.py
COUNSELING_SUPPORT = {
    "assessment_flow": {
        "mental_health": {
            "screening_questions": [
                "How long have you been feeling this way?",
                "Is this affecting your daily activities?"
            ],
            "response": {
                "non_crisis": "Licensed therapists: 555-4321",
                "crisis": "Immediate help: 988 Suicide & Crisis Lifeline"
            },
            "keywords": ["depressed", "anxious", "panic"]
        },
        "relationships": {
            "screening_questions": [
                "What's the main challenge in this relationship?",
                "Have you considered professional mediation?"
            ],
            "response": "Relationship experts: 555-8765",
            "keywords": ["marriage", "divorce", "family"]
        }
    },
    "follow_up": {
        "resources": [
            "Download our counseling preparation guide: https://example.com/guide",
            "Weekly support groups schedule: https://example.com/groups"
        ]
    }
}
