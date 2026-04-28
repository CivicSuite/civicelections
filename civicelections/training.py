"""Election worker training Q&A support."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingAnswer:
    topic: str
    steps: tuple[str, ...]
    supervisor_review_required: bool


def answer_worker_training_question(topic: str, procedures: list[str]) -> TrainingAnswer:
    steps = tuple(step.strip() for step in procedures if step.strip()) or ("Use the official procedures manual.",)
    return TrainingAnswer(topic.strip(), steps, True)
