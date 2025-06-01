from p_and_c_config import PRAYER_SUPPORT, COUNSELING_SUPPORT


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
