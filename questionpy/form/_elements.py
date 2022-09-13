from typing import Annotated, List, Literal, Union, Optional, get_args

from pydantic import BaseModel, Field
from typing_extensions import TypeGuard

__all__ = ["StaticTextElement", "TextInputElement", "CheckboxElement", "CheckboxGroupElement", "RadioGroupElement",
           "SelectElement", "HiddenElement", "GroupElement", "FormElement", "FormSection", "Form", "is_form_element"]


class _Labelled(BaseModel):
    label: str


class _Named(BaseModel):
    name: str


class StaticTextElement(_Labelled, _Named):
    kind: Literal["static_text"] = "static_text"
    text: str


class TextInputElement(_Labelled, _Named):
    kind: Literal["input"] = "input"
    required: bool = False
    default: Optional[str] = None
    placeholder: Optional[str] = None


class CheckboxElement(_Named):
    kind: Literal["checkbox"] = "checkbox"
    left_label: Optional[str] = None
    right_label: Optional[str] = None
    required: bool = False
    selected: bool = False


class CheckboxGroupElement(BaseModel):
    kind: Literal["checkbox_group"] = "checkbox_group"
    checkboxes: List[CheckboxElement]


class RadioGroupElement(_Labelled, _Named):
    class Option(BaseModel):
        label: str
        value: str
        selected: bool = False

    kind: Literal["radio_group"] = "radio_group"
    options: List[Option]
    required: bool = False


class SelectElement(_Labelled, _Named):
    class Option(BaseModel):
        label: str
        value: str
        selected: bool = False

    kind: Literal["select"] = "select"
    multiple: bool = False
    options: List[Option]
    required: bool = False


class HiddenElement(_Named):
    kind: Literal["hidden"] = "hidden"
    value: str


class GroupElement(_Labelled, _Named):
    kind: Literal["group"] = "group"
    elements: List["FormElement"]


FormElement = Annotated[
    Union[
        StaticTextElement, TextInputElement, CheckboxElement, CheckboxGroupElement,
        RadioGroupElement, SelectElement, HiddenElement, GroupElement
    ],
    Field(discriminator="kind")
]

GroupElement.update_forward_refs()


class FormSection(BaseModel):
    header: str
    elements: List[FormElement] = []


class Form(BaseModel):
    general: List[FormElement] = []
    sections: List[FormSection] = []


def is_form_element(value: object) -> TypeGuard[FormElement]:
    # unions don't support runtime type checking through isinstance
    # this checks if value is an instance of any of the union members
    return isinstance(value, get_args(get_args(FormElement)[0]))
