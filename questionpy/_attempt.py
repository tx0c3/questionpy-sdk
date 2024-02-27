from abc import ABC, abstractmethod
from functools import cached_property
from typing import ClassVar, Generic, TypeVar, Optional

import jinja2
from pydantic import BaseModel, ConfigDict
from questionpy_common.api.attempt import BaseAttempt, Score, AttemptModel, AttemptUi

from ._ui import create_jinja2_environment

_Q = TypeVar("_Q", bound="Question")
_S = TypeVar("_S", bound=Score)
_AS = TypeVar("_AS", bound="BaseAttemptState")


class BaseAttemptState(BaseModel):
    model_config = ConfigDict(extra="allow")

    variant: int


class Attempt(BaseAttempt, ABC, Generic[_Q, _S, _AS]):
    score_class: ClassVar[type[_S]] = Score
    state_class: ClassVar[type[_AS]] = BaseAttemptState

    def __init__(self, question: _Q, state: _AS, response: Optional[dict] = None, score: Optional[_S] = None) -> None:
        self.question = question
        self.state = state
        self.response = response
        self.score = score

    @abstractmethod
    def render_ui(self) -> AttemptUi:
        pass

    @cached_property
    def jinja2(self) -> jinja2.Environment:
        return create_jinja2_environment(self, self.question, self.question.qtype)

    def export(self) -> AttemptModel:
        return AttemptModel(
            variant=self.variant,
            ui=self.render_ui()
        )

    def export_attempt_state(self) -> str:
        return self.state.model_dump_json()
