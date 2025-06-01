from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from rapidfuzz import process, fuzz
import re
from langchain.schema import HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from traceback import format_tb

load_dotenv('.env')
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class IntentHandler:
    @staticmethod
    def detect_intent(user_input, intents, threshold=50):
        """Fuzzy-match based intent detection"""
        user_input = user_input.strip().lower()
        best_match = process.extractOne(
            user_input, intents.keys(), scorer=fuzz.WRatio)
        return best_match[0] if best_match and best_match[1] >= threshold else None


class MultimediaHandler:
    INTENTS = {
        "play_video": {"triggers": ["video", "watch", "stream"], "response": "Here's your video: [VIDEO_URL]"},
        "play_song": {"triggers": ["song", "music", "play"], "response": "Playing song: [SONG_URL]"}
    }

    @classmethod
    def handle(cls, user_input):
        intent = IntentHandler.detect_intent(user_input, cls.INTENTS)
        if intent:
            return cls.INTENTS[intent]["response"]
        return None


class SpiritualFlowManager:
    TRIGGER_WORDS = {"sad", "depressed", "anxious", "stress",
                     "pain", "confused", "afraid", "sick", "hurt",
                     "scared", "angry", "enraged"}

    @classmethod
    def needs_spiritual_help(cls, text: str):
        return any(word in text.lower() for word in cls.TRIGGER_WORDS)


class EnhancedPrayerCounselor:
    def __init__(self):
        self.PRAYER_TOPICS = {
            "marriage": {
                "verses": ["1 Corinthians 13:4-7", "Ephesians 4:2-3", "Proverbs 3:3-4"],
                "prayer": "Lord, strengthen this union with patience and understanding. Help them love as You love. Amen.",
                "contact": "National Marriage Hotline: 1-800-327-4357"
            },
            "health": {
                "verses": ["Jeremiah 30:17", "3 John 1:2", "Psalm 103:2-3"],
                "prayer": "Heavenly Father, bring restoration and wholeness. Guide medical staff and comfort the afflicted. Amen.",
                "contact": "Christian Medical Association: 1-888-230-2637"
            },
            "anxiety": {
                "verses": ["Philippians 4:6-7", "1 Peter 5:7", "Matthew 6:34"],
                "prayer": "Prince of Peace, calm troubled hearts. Help them cast all cares on You. Amen.",
                "contact": "NAMI Helpline: 1-800-950-6264"
            },
            "parenting": {
                "verses": ["Proverbs 22:6", "Psalm 127:3", "Deuteronomy 6:6-7"],
                "prayer": "Loving God, grant wisdom and patience. Help raise children in Your ways. Amen.",
                "contact": "Focus on the Family: 1-800-A-FAMILY"
            },
            "default": {
                "verses": ["Proverbs 22:6", "Psalm 127:3", "Deuteronomy 6:6-7"],
                "prayer": "Father Lord help me to pray",
                "contact": "Focus on the prayer: 1-800-A-FAMILY",
                "guide": "for more precision you could enter prayer for marriage, health, anxiety, parenting"
            }
        }

        self.COUNSELING_RESOURCES = {
            "grief": {
                "verses": ["Psalm 34:18", "Revelation 21:4", "Matthew 5:4"],
                "steps": [
                    "Allow yourself to grieve",
                    "Join support group",
                    "Memorialize your loss"
                ],
                "counseling": "GriefShare: 1-800-395-5755"
            },
            "addiction": {
                "verses": ["1 Corinthians 10:13", "Philippians 4:13", "Galatians 5:1"],
                "steps": [
                    "Contact Celebrate Recovery",
                    "Remove triggers",
                    "Daily accountability"
                ],
                "counseling": "SAMHSA: 1-800-662-4357"
            },
            "relationships": {
                "verses": ["Colossians 3:13", "Ecclesiastes 4:9-12", "Proverbs 15:1"],
                "steps": [
                    "Practice active listening",
                    "Set healthy boundaries",
                    "Seek couples counseling"
                ],
                "counseling": "Christian Relationship Counselors Network: 1-855-222-2575"
            },
            "default": {
                "verses": ["Colossians 3:13", "Ecclesiastes 4:9-12", "Proverbs 15:1"],
                "steps": [
                    "Practice active listening",
                    "Set healthy boundaries",
                    "Seek couples counseling"
                ],
                "counseling": "Christian Counselors Network: 1-855-222-2575"
            }
        }

        self.CRISIS_KEYWORDS = {
            "suicide": "988 Suicide & Crisis Lifeline",
            "abuse": "National Domestic Violence Hotline: 1-800-799-7233",
            "emergency": "Call 911 immediately",
            "domestic violence": "Call domestic violence service 1-222-33-1222"
        }

    def _fuzzy_match(self, query, options):
        result = process.extractOne(
            str(query), list(options), scorer=fuzz.WRatio)
        return result[0] if result and result[1] > 75 else None

    def handle_crisis(self, user_input):
        for keyword, resource in self.CRISIS_KEYWORDS.items():
            if keyword in user_input.lower():
                return f"IMPORTANT: {resource}. Please reach out now. I'm praying for you."
        return None

    def get_prayer_response(self, topic):
        topic = self._fuzzy_match(topic, list(self.PRAYER_TOPICS.keys()))
        if topic is None:
            data = self.PRAYER_TOPICS["default"]
            return (
                f"Scripture: {', '.join(data['verses'])}\n"
                f"Prayer: {data['prayer']}\n"
                f"Guide: {data['guide']}\n"
                f"Support: {data['contact']}"
            )

        if topic not in list(self.PRAYER_TOPICS.keys()):
            data = self.PRAYER_TOPICS["default"]
            return (
                f"Scripture: {', '.join(data['verses'])}\n"
                f"Prayer: {data['prayer']}\n"
                f"Guide: {data['guide']}\n"
                f"Support: {data['contact']}"
            )

        data = self.PRAYER_TOPICS[topic]
        return (
            f"Scripture: {', '.join(data['verses'])}\n"
            f"Prayer: {data['prayer']}\n"
            f"Support: {data['contact']}"
        )

    def get_counseling_response(self, issue):
        issue = self._fuzzy_match(issue, list(
            self.COUNSELING_RESOURCES.keys()))
        if issue is None:
            data = self.COUNSELING_RESOURCES["default"]
            return (
                f"Biblical Guidance: {', '.join(data['verses'])}\n"
                f"Practical Steps:\n- " + "\n- ".join(data['steps']) + "\n"
                f"Professional Help: {data['counseling']}"
            )

        if issue not in list(self.COUNSELING_RESOURCES.keys()):
            data = self.COUNSELING_RESOURCES["default"]
            return (
                f"Biblical Guidance: {', '.join(data['verses'])}\n"
                f"Practical Steps:\n- " + "\n- ".join(data['steps']) + "\n"
                f"Professional Help: {data['counseling']}"
            )

        data = self.COUNSELING_RESOURCES[issue]
        return (
            f"Biblical Guidance: {', '.join(data['verses'])}\n"
            f"Practical Steps:\n- " + "\n- ".join(data['steps']) + "\n"
            f"Professional Help: {data['counseling']}"
        )

    def _extract_topic(self, text, intent):
        """Advanced topic extraction with context awareness"""
        # Remove common intent-related words
        text = text.lower().strip()
        removal_patterns = {
            "prayer": r"\b(pray|prayer|request|need|for|about)\b",
            "counseling": r"\b(counsel|advice|guidance|help|with)\b"
        }

        # Clean the text
        cleaned_text = re.sub(removal_patterns[intent], "", text)

        # Find candidate phrases
        candidates = re.findall(r"\b(\w+\s*?){1,3}$", cleaned_text)
        if not candidates:
            candidates = re.findall(r"for\s+([\w\s]+)", text)

        # Fuzzy match with known topics
        topics = self.PRAYER_TOPICS if intent == "prayer" else self.COUNSELING_RESOURCES
        if candidates:
            best_match = process.extractOne(
                candidates[0], topics.keys(), scorer=fuzz.WRatio)
            if best_match and best_match[1] > 65:
                return best_match[0]
            else:
                return candidates[0]

        # Fallback to first noun phrase
        nouns = re.findall(
            # AKACHI: When adding additinal fucntions edit this regex expression
            r"\b(marriage|health|anxiety|parenting|grief|addiction|relationships)\b", text)
        return nouns[0] if nouns else None

    def _detect_intent(self, user_input):
        """Advanced intent detection with context awareness"""
        # Normalize input
        clean_input = user_input.lower().strip()
        if clean_input == 'prayer':
            return ('prayer', None, 1.0)
        elif clean_input in ['counselling', 'counseling', 'conselling']:
            return ('counseling', None, 1.0)

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
                "primary": ["counsel", "advice", "guidance", 'counselling'],
                "secondary": ["need", "seek", "want", 'counselling', 'counseling'],
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


class SpiritualAssistant:
    def __init__(self):
        self.counselor = EnhancedPrayerCounselor()
        self.memory = ConversationBufferMemory()
        self.in_chain = False
        self.topic = None
        self.intent = None
        self.in_flow = False  # Tracks conversation state
        self.selection = None

        # self.llm = OpenAI(temperature=0.7, api_key=OPENAI_API_KEY)
        # self.prompt = PromptTemplate(
        #     input_variables=["history", "input"],
        #     template="""As a Christian assistant, respond with compassion and wisdom.
        #     Current conversation:
        #     {history}
        #     Person: {input}
        #     Assistant:"""
        # )

    def get_response(self, user_input: str):
        try:
            # Process input through counselor
            # if self.in_flow and self.selection:
            #     if self.selection == 'prayer':
            #         topic = self.counselor._fuzzy_match(
            #             user_input.lower(), self.counselor.PRAYER_TOPICS.keys())
            #         if not topic:
            #             data = self.counselor.PRAYER_TOPICS["default"]
            #             return (
            #                 f"Scripture: {', '.join(data['verses'])}\n"
            #                 f"Prayer: {data['prayer']}\n"
            #                 f"Guide: {data['guide']}\n"
            #                 f"Support: {data['contact']}"
            #             )

            #         data = self.counselor.PRAYER_TOPICS[topic]
            #         self.in_flow = False
            #         return (
            #             f"Scripture: {', '.join(data['verses'])}\n"
            #             f"Prayer: {data['prayer']}\n"
            #             f"Support: {data['contact']}"
            #         )

            #     elif self.selection == 'counseling':
            #         issue = self._fuzzy_match(
            #             issue, self.counselor.COUNSELING_RESOURCES.keys())
            #         if not issue:
            #             data = self.counselor.COUNSELING_RESOURCES["default"]
            #             return (
            #                 f"Biblical Guidance: {', '.join(data['verses'])}\n"
            #                 f"Practical Steps:\n- " +
            #                 "\n- ".join(data['steps']) + "\n"
            #                 f"Professional Help: {data['counseling']}"
            #             )

            #         data = self.counselor.COUNSELING_RESOURCES[issue]
            #         self.in_flow = False
            #         return (
            #             f"Biblical Guidance: {', '.join(data['verses'])}\n"
            #             f"Practical Steps:\n- " +
            #             "\n- ".join(data['steps']) + "\n"
            #             f"Professional Help: {data['counseling']}"
            #         )

            if self.intent and self.topic is None:
                # self.topic = user_input
                # if self.intent == "prayer":
                #     response = self.counselor.get_prayer_response(self.topicsession

                # elif self.intent == "counseling":
                self.topic = self.counselor._extract_topic(
                    user_input, self.intent)
                # response = self.counselor.get_counseling_response(
                #     self.topic)
                if self.intent == 'prayer':
                    response = self.counselor.get_prayer_response(self.topic)
                elif self.intent == 'counseling':
                    response = self.counselor.get_counseling_response(
                        self.topic)
                self.in_chain = False
                return response

            crisis_response = self.counselor.handle_crisis(user_input)
            if crisis_response:
                self.in_chain = False
                print(crisis_response)
                return crisis_response

            # Detect intent
            intent, topic, confidence = self.counselor._detect_intent(
                user_input)

            # if confidence > 0.7:
            if intent == "prayer":
                self.intent = intent
                if not topic:
                    self.topic = None
                    return (
                        "prayer for what?\n"
                        "e.g prayer for marriage, prayer for health, prayer for anxiety, prayer for parenting\n"
                    )

                response = self.counselor.get_prayer_response(topic)
                self.in_chain = False
                self.topic = topic
                return response

            elif intent == "counseling":
                self.intent = intent
                if not topic:
                    self.topic = None
                    return (
                        "counselling for what?\n"
                        "e.g counselling for grief, counselling for addiction, counselling for anxiety\n"
                    )

                response = self.counselor.get_counseling_response(topic)
                self.in_chain = False
                self.topic = topic
                return response

            else:
                # Check if user enters no, noe, nerver e.t.c and also
                # checks if the user enters word similar to it
                response = user_input.lower().strip().replace('_', ' ')
                self.in_chain = False
                is_no = process.extractOne(
                    response, ['no', 'nope', 'none', 'never', 'absolutely not'])

                if is_no and is_no[1] > 75:
                    return "Okay"

                response = ("Entry must be either prayer or counselling\n"
                            "Or requesting for prayer or counselling with a topic\n"
                            "e.g prayer for marriage, counselling for grief")

                return response

                # Fallback to LLM with spiritual context
                # if not response:
                #     chain = LLMChain(
                #         llm=self.llm,
                #         prompt=self.prompt,
                #         memory=self.memory
                #     )
                #     response = chain.run(input=user_input)
                #     self.in_chain = False
                #     return response

        except Exception as e:
            self.in_chain = False
            return f"Error: {str(e)}. Let's try again."


class MultiFunctionalAssistant:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7, api_key=OPENAI_API_KEY)
        self.memory = ConversationBufferMemory()
        self.spiritual_assistant = SpiritualAssistant()
        self.media_handler = MultimediaHandler()

    def get_response(self, user_input):
        try:
            # Check media intents first
            # Too trigger enter i want to to watch stream and video

            if self.spiritual_assistant.in_chain:
                response = self.spiritual_assistant.get_response(user_input)

                self.memory.save_context(
                    {"input": str(user_input)},
                    {"output": str(response)}
                )

                return response

            media_res = self.media_handler.handle(user_input)
            if media_res:
                return media_res

            # Main processing
            # response = self.llm.generate(
            #     [user_input]).generations[0][0].text.strip()
            response = "Okay.."

            # Detect prayer or counselling needs
            if SpiritualFlowManager.needs_spiritual_help(user_input):
                response += "\nWould you like prayer or counseling support?, if not reply with no"
                # Initiate spiritual flow
                self.spiritual_assistant.in_chain = True

            # Continue spiritual flow if active

            # Save context
            self.memory.save_context(
                {"input": str(user_input)},
                {"output": str(response)}
            )

            return response

        except Exception as e:
            return f"System error: Please rephrase your request.{"/n".join(format_tb(e.__traceback__))}"


# Usage Example
if __name__ == "__main__":
    assistant = MultiFunctionalAssistant()

    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break

        response = assistant.get_response(user_input)
        # response = assistant.media_handler.handle(user_input)
        print(f"Assistant: {response}")
