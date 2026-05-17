import re
import time
from collections import Counter

from django.conf import settings

STOP_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "if",
    "then",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "as",
    "by",
    "at",
    "from",
    "that",
    "this",
    "it",
    "its",
    "into",
    "can",
    "will",
    "would",
    "should",
    "could",
    "about",
    "how",
    "using",
    "use",
    "users",
    "user",
    "their",
    "they",
    "them",
    "we",
    "our",
    "you",
    "your",
}


POSITIVE_WORDS = {
    "good",
    "great",
    "excellent",
    "amazing",
    "positive",
    "happy",
    "love",
    "fast",
    "successful",
    "success",
    "improve",
    "improved",
    "helpful",
    "efficient",
    "reliable",
    "clean",
    "strong",
    "easy",
    "better",
}


NEGATIVE_WORDS = {
    "bad",
    "poor",
    "terrible",
    "negative",
    "sad",
    "hate",
    "slow",
    "failed",
    "failure",
    "error",
    "problem",
    "difficult",
    "hard",
    "worse",
    "bug",
    "broken",
    "issue",
    "unreliable",
}


def summarize_text(input_text):
    sentences = re.split(r"(?<=[.!?])\s+", input_text.strip())
    selected_sentences = sentences[:2]

    summary = " ".join(selected_sentences)

    return {
        "summary": summary,
        "metadata": {
            "processor": "mock_summarizer_v1",
            "sentence_count": len([s for s in sentences if s.strip()]),
            "summary_sentence_count": len(selected_sentences),
        },
    }


def analyze_sentiment(input_text):
    words = _extract_words(input_text)

    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)

    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "score": {
            "positive_words": positive_count,
            "negative_words": negative_count,
        },
        "metadata": {
            "processor": "mock_sentiment_v1",
            "word_count": len(words),
        },
    }


def generate_tags(input_text):
    words = _extract_words(input_text)

    filtered_words = [
        word for word in words if word not in STOP_WORDS and len(word) > 3
    ]

    most_common_words = Counter(filtered_words).most_common(5)
    tags = [word for word, count in most_common_words]

    return {
        "tags": tags,
        "metadata": {
            "processor": "mock_tag_generator_v1",
            "candidate_word_count": len(filtered_words),
        },
    }


def process_text(task_type, input_text):
    """
    Router function for supported text processors.
    Keeps Celery task independent from individual processor implementations.
    """

    # to simulate a long-running AI/media processing task
    time.sleep(10)

    # simulate processing failures to test retry handling
    if settings.DEBUG and "force_fail" in input_text.lower():
        raise ValueError("Forced failure for testing retry handling.")

    processors = {
        "summarization": summarize_text,
        "sentiment": analyze_sentiment,
        "tag_generation": generate_tags,
    }

    processor = processors.get(task_type)

    if processor is None:
        raise ValueError(f"Unsupported task type: {task_type}")

    return processor(input_text)


def _extract_words(input_text):
    return re.findall(r"\b[a-zA-Z]+\b", input_text.lower())