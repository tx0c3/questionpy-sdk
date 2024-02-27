#  This file is part of the QuestionPy SDK. (https://questionpy.org)
#  The QuestionPy SDK is free software released under terms of the MIT license. See LICENSE.md.
#  (c) Technische Universität Berlin, innoCampus <info@isis.tu-berlin.de>

from abc import ABC
from typing import Optional, Type, Generic, TypeVar, cast, ClassVar

from pydantic import BaseModel, ConfigDict
from questionpy_common.api.qtype import BaseQuestionType
from questionpy_common.api.question import BaseQuestion

from ._attempt import Attempt
from .form import FormModel, OptionsFormDefinition

_F = TypeVar("_F", bound=FormModel)
_A = TypeVar("_A_co", bound=Attempt)
_Q = TypeVar("_Q_co", bound="Question")
_QS = TypeVar("_QS", bound="BaseQuestionState")

class BaseQuestionState(BaseModel, Generic[_F]):
    model_config = ConfigDict(extra='allow')

    options: _F


class Question(BaseQuestion, ABC, Generic[_QS, _A]):
    state_class: ClassVar[type[_QS]] = BaseQuestionState
    attempt_class: ClassVar[type[_A]]

    def __init__(self, qtype: BaseQuestionType, state: _QS) -> None:
        self.qtype = qtype
        self.state = state

    def start_attempt(self, variant: int) -> _A:
        attempt_state = self.attempt_class.state_class(variant=variant)
        return self.attempt_class(self, attempt_state)

    def get_attempt(self, attempt_state: str, scoring_state: Optional[str] = None,
                    response: Optional[dict] = None, compute_score: bool = False,
                    generate_hint: bool = False) -> _A:
        parsed_state = self.attempt_class.state_class.model_validate_json(attempt_state)
        parsed_score = self.attempt_class.score_class.model_validate_json(scoring_state) if scoring_state else None

        return self.attempt_class(question, parsed_state, response, parsed_score)

    def __init_subclass__(cls, *args: object, **kwargs: object) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not hasattr(cls, "attempt_class") or not issubclass(cls.attempt_class, Attempt):
            raise AttributeError("TODO")  # TODO

    def export_question_state(self) -> str:
        return self.state.model_dump_json()


class QuestionType(BaseQuestionType, Generic[_F, _Q]):
    """A question type.

    This class is intended to be used in one of two ways:
    - If you don't need to override any of the default :class:`QuestionType` methods, you should provide your
      :class:`FormModel` and :class:`Question` subclasses as constructor arguments.
    - If you do, you should inherit from :class:`QuestionType`, specifying your :class:`FormModel` and :class:`Question`
      as type arguments:

      >>> class MyOptions(FormModel): ...
      >>> class MyAttempt(Attempt): ...
      >>> class MyQuestion(Question[DefaultQuestionState[MyOptions], MyAttempt]): ...
      >>> class MyQuestionType(QuestionType[MyOptions, MyQuestion]):
      ...   ...  # Your code goes here.
    """

    options_class: Type[_F] = FormModel
    question_class: Type[_Q]

    def __init_subclass__(cls, *args: object, **kwargs: object) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not hasattr(cls, "question_class") or not issubclass(cls.question_class, Question):
            raise RuntimeError("TODO")  # TODO

    def get_options_form(self, question: Optional[_Q]) -> tuple[OptionsFormDefinition, dict[str, object]]:
        if question:
            form_data = question.state.options.model_dump(mode="json")
        else:
            form_data = {}

        return (self.options_class.qpy_form, form_data)

    def create_question_from_state(self, question_state: str) -> _Q:
        state_class = self.question_class.state_class
        if state_class is BaseQuestionState:
            # If the question is using the default question state, the "options" attribute will deserialize to an empty
            # FormModel, but we want the correct options class.
            state_class = state_class[self.options_class]

        parsed_state = self.question_class.state_class.model_validate_json(question_state)
        return cast(_Q, self.question_class(self, parsed_state))

    def create_question_from_options(self, form_data: dict[str, object], old_question: Optional[_Q] = None) -> _Q:
        try:
            parsed_form_data = self.options_class.model_validate(form_data)
        except ValidationError as e:
            error_dict = {".".join(map(str, error["loc"])): error["msg"] for error in e.errors()}
            raise OptionsFormValidationError(error_dict) from e

        state = self.question_class.state_class(options=parsed_form_data)

        return cast(_Q, self.question_class(self, state))
