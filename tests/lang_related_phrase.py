import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv('.env')

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class TopicValidator:
    def __init__(self):
        self.embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        self.allowed_topics = {
            "stress_management": ["stress", "anxiety", "burnout", "work pressure"],
            "spiritual_growth": ["prayer", "faith", "scripture study", "meditation"],
            "relationships": ["marriage", "family conflict", "parenting", "friendship"]
        }
        self.blocklist = {
            "lgbtq+", "gay", "lesbian",
            "trangender", "queer", "bisexual"
        }
        self.topic_embeddings = self._precompute_embeddings()
        self.similarity_threshold = 0.8  # Adjust based on testing

    def _precompute_embeddings(self):
        """Convert allowed topics to embeddings during initialization"""
        embeddings = []

        # Create embeddings for each category and its keywords
        for category, keywords in self.allowed_topics.items():
            # Embed category name
            embeddings.append(self.embeddings_model.embed_query(category))

            # Embed individual keywords
            for keyword in keywords:
                embeddings.append(self.embeddings_model.embed_query(keyword))

        return np.array(embeddings)

    def _get_query_embedding(self, query: str) -> np.ndarray:
        """Convert user query to embedding vector"""
        return np.array(self.embeddings_model.embed_query(query))

    def calculate_similarity(self, query: str) -> dict:
        """Calculate similarity scores against all allowed topics"""
        query_embedding = self._get_query_embedding(query)
        similarities = cosine_similarity(
            [query_embedding],
            self.topic_embeddings
        )[0]

        return {
            "max_score": np.max(similarities).item(),
            "average_score": np.mean(similarities).item(),
            "category_scores": {
                category: np.max(
                    similarities[i*len(keywords):(i+1)*len(keywords)])
                for i, (category, keywords) in enumerate(self.allowed_topics.items())
            }
        }

    def contains_blocked_terms(self, query: str) -> bool:
        query_lower = query.lower()
        return any(term in query_lower for term in self.blocklist)

    def is_topic_allowed(self, query: str) -> bool:
        """Determine if query matches allowed topics semantically"""
        if self.contains_blocked_terms(query):
            return False

        scores = self.calculate_similarity(query)
        return scores["max_score"] >= self.similarity_threshold

    def explain_similarity(self, query: str) -> dict:
        """Provide detailed similarity analysis"""
        scores = self.calculate_similarity(query)
        explanation = {
            "query": query,
            "threshold": self.similarity_threshold,
            "decision": "allowed" if scores["max_score"] >= self.similarity_threshold else "rejected",
            "scores": scores
        }
        return explanation

    def add_topic_category(self, category: str, keywords: list):
        """Add new topic category at runtime"""
        self.allowed_topics[category] = keywords
        new_embeddings = [self.embeddings_model.embed_query(category)]
        new_embeddings.extend(
            [self.embeddings_model.embed_query(kw) for kw in keywords])
        self.topic_embeddings = np.vstack(
            [self.topic_embeddings, new_embeddings])


validator = TopicValidator()

queries = [
    "I'm feeling overwhelmed at work",
    "How do I start daily bible reading?",
    "Explain quantum field theory",
    "tell me about Jesus",
    "Tell me about dinosaurs",
    "What does the bible say about being gay"
]

for query in queries:
    result = validator.explain_similarity(query)
    print(f"Query: {query}")
    print(f"Decision: {result['decision']}")
    print(f"Max Score: {result['scores']['max_score']:.2f}")
    print(f"Category Scores:")
    for cat, score in result['scores']['category_scores'].items():
        print(f"- {cat}: {score:.2f}")
    print("\n")
