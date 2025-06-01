from rapidfuzz import process, fuzz
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
import re


class EnhancedPrayerCounselor:
    def __init__(self):
        # ... (keep previous resource dictionaries)
        self.llm = OpenAI(temperature=0.7)
        self.memory = ConversationBufferMemory()
        self.counselor = EnhancedPrayerCounselor()

    def _detect_intent(self, user_input):
        """Advanced intent detection with context awareness"""
        # Normalize input
        clean_input = user_input.lower().strip()

        # Crisis detection first
        crisis_match = self.handle_crisis(clean_input)
        if crisis_match:
            return ("crisis", None, 1.0)

        # Define intent signals with weights
        intent_signals = {
            "prayer": {
                "primary": ["pray", "prayer", "praying"],
                "secondary": ["request", "need", "please"],
                "weight": 2.0
            },
            "counseling": {
                "primary": ["counsel", "advice", "guidance"],
                "secondary": ["need", "seek", "want"],
                "weight": 1.5
            }
        }

        # Calculate intent scores
        scores = {"prayer": 0.0, "counseling": 0.0}

        # Check for exact phrase patterns
        phrase_patterns = {
            "prayer": [
                r"pray\s+for\s+(.+)",
                r"prayer\s+request\s+for\s+(.+)",
                r"need\s+prayer\s+for\s+(.+)"
            ],
            "counseling": [
                r"counseling\s+for\s+(.+)",
                r"advice\s+on\s+(.+)",
                r"help\s+with\s+(.+)"
            ]
        }

        # Check phrase patterns first
        detected_intent = None
        topic = None
        for intent, patterns in phrase_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, clean_input)
                if match:
                    detected_intent = intent
                    topic = match.group(1).strip()
                    return (detected_intent, topic, 1.0)

        # Calculate weighted keyword scores
        tokens = clean_input.split()
        for token in tokens:
            for intent, signals in intent_signals.items():
                # Check primary keywords
                primary_match = process.extractOne(
                    token, signals["primary"], scorer=fuzz.WRatio)
                if primary_match and primary_match[1] > 85:
                    scores[intent] += 3.0 * signals["weight"]

                # Check secondary keywords
                secondary_match = process.extractOne(
                    token, signals["secondary"], scorer=fuzz.WRatio)
                if secondary_match and secondary_match[1] > 75:
                    scores[intent] += 1.0 * signals["weight"]

        # Determine dominant intent
        max_score = max(scores.values())
        if max_score > 5.0:
            detected_intent = max(scores, key=scores.get)

            # Extract topic using advanced pattern
            topic = self._extract_topic(clean_input, detected_intent)

            return (detected_intent, topic, max_score/10)

        return (None, None, 0.0)
