from questionpy import (
    Attempt,
    AttemptUiPart,
    BaseAttemptState,
    BaseQuestionState,
    BaseScoringState,
    Question,
    QuestionType,
    ScoringCode,
)
from questionpy_common.api.attempt import BaseAttempt, ScoreModel
from questionpy_common.api.question import QuestionModel, ScoringMethod

from .form import MyModel


class MyAttemptState(BaseAttemptState):
    custom_field: str


class MyScoringState(BaseScoringState):
    custom_field: int


class ExampleAttempt(Attempt):
    attempt_state: MyAttemptState
    scoring_state: MyScoringState | None

    def export_score(self) -> ScoreModel:
        if self.scoring_state:
            self.scoring_state.custom_field += 1
        else:
            self.scoring_state = MyScoringState(custom_field=1)

        if not self.response or "choice" not in self.response:
            return ScoreModel(scoring_code=ScoringCode.RESPONSE_NOT_SCORABLE, score=None,
                              scoring_state=self.scoring_state.model_dump_json())

        if self.response["choice"] == "B":
            return ScoreModel(scoring_code=ScoringCode.AUTOMATICALLY_SCORED, score=1,
                              scoring_state=self.scoring_state.model_dump_json())

        return ScoreModel(scoring_code=ScoringCode.AUTOMATICALLY_SCORED, score=0,
                          scoring_state=self.scoring_state.model_dump_json())

    def render_formulation(self) -> AttemptUiPart:
        return AttemptUiPart(
            content=self.jinja2.get_template("local.example/formulation.xhtml.j2").render(),
            placeholders={"description": "Welcher ist der zweite Buchstabe im deutschen Alphabet?"},
        )

    def render_general_feedback(self) -> AttemptUiPart:
        return AttemptUiPart(content=self.jinja2.get_template("local.example/feedback.xhtml.j2").render())


class MyQuestionState(BaseQuestionState[MyModel]):
    custom_field: str


class ExampleQuestion(Question):
    attempt_class = ExampleAttempt

    options: MyModel
    state: MyQuestionState

    def start_attempt(self, variant: int) -> BaseAttempt:
        return ExampleAttempt(self, MyAttemptState(variant=variant, custom_field="something"))

    def export(self) -> QuestionModel:
        return QuestionModel(scoring_method=ScoringMethod.AUTOMATICALLY_SCORABLE)


class ExampleQuestionType(QuestionType):
    question_class = ExampleQuestion

    def create_question_from_options(self, old_state: str | None, form_data: dict[str, object]) -> Question:
        return ExampleQuestion(
            self,
            MyQuestionState(
                package_name="abc",
                package_version="1.2.3",
                options=MyModel.model_validate(form_data),
                custom_field="something",
            ),
        )
