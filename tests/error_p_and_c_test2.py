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


def handle_prayer(request: str) -> dict:
    """Enhanced prayer handler with multiple response components"""
    request_lower = request.lower()
    response = {"type": "default"}

    # Detect prayer category
    for category, data in PRAYER_SUPPORT["categories"].items():
        if any(keyword in request_lower for keyword in data.get("keywords", [])):
            response = {
                "type": "categorized",
                "category": category,
                "components": {
                    "immediate_response": data["response"],
                    "scripture": data["scripture"],
                    "prayer": data["auto_prayer"],
                    "escalation": PRAYER_SUPPORT["escalation_paths"]
                }
            }
            break

    # Crisis detection
    if any(word in request_lower for word in ["suicide", "emergency", "urgent"]):
        response["components"]["escalation"] = PRAYER_SUPPORT["escalation_paths"]["crisis"]

    return response


def handle_counseling(request: str, history: list) -> dict:
    """Multi-stage counseling support system"""
    request_lower = request.lower()
    response = {"stage": "initial"}

    # Initial request handling
    if "counseling" in request_lower or "therapy" in request_lower:
        response.update({
            "stage": "category_selection",
            "message": "What type of counseling are you seeking?",
            "options": list(COUNSELING_SUPPORT["assessment_flow"].keys())
        })

    # Conversation context analysis
    context = " ".join([msg["content"] for msg in history[-3:]])

    # Category-specific handling
    for category, data in COUNSELING_SUPPORT["assessment_flow"].items():
        if any(keyword in context for keyword in data["keywords"]):
            response.update({
                "stage": "screening",
                "category": category,
                "questions": data["screening_questions"],
                "resources": data["response"],
                "follow_up": COUNSELING_SUPPORT["follow_up"]
            })

            # Crisis detection
            if any(word in context for word in ["suicide", "self-harm"]):
                response["resources"] = data["response"]["crisis"]
                response["stage"] = "crisis"

    return response


class SupportAssistant:
    def generate_response(self, user_input):
        # Previous implementation

        # Enhanced Prayer Handling
        if "prayer" in response.lower():
            prayer_data = handle_prayer(user_input)
            response = f"""
            {prayer_data['components']['prayer']}
            
            Scripture Reference: {prayer_data['components']['scripture']}
            Contact: {prayer_data['components']['immediate_response']}
            
            Additional Options:
            - {prayer_data['components']['escalation']}
            - {PRAYER_SUPPORT['escalation_paths']['follow_up']}
            """

        # Enhanced Counseling Flow
        elif "counseling" in response.lower():
            counseling_data = handle_counseling(
                user_input, self.memory.get_history())

            if counseling_data["stage"] == "screening":
                response = f"""
                Let's start with a few questions:
                {''.join(f'\n- {q}' for q in counseling_data['questions'])}
                
                When ready: {counseling_data['resources']}
                """

            elif counseling_data["stage"] == "crisis":
                response = f"""
                ⚠️ Immediate Assistance:
                {counseling_data['resources']}
                
                Additional Resources:
                {''.join(f'\n- {r}' for r in counseling_data['follow_up']['resources'])}
                """

        return response
