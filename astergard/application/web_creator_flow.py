from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from astergard.characters.appearance import appearance_profile_from_choices, appearance_steps_for_gender, gender_step, normalize_gender_id
from astergard.characters.creation import (
    BIRTH_REGION_DEFINITIONS,
    CHILDHOOD_DEFINITIONS,
    ORIGIN_DEFINITIONS,
    birth_region_prompt_text,
    childhood_prompt_text,
    resolve_childhood,
    resolve_origin,
    resolve_birth_region,
    origin_prompt_text,
    validate_age,
    validate_text,
)
from astergard.characters.creation import CharacterCreationError
from astergard.characters.creation import CharacterCreationProfile
from astergard.characters.professions import ADDITIONAL_PROFESSIONS, MAIN_PROFESSIONS, ProfessionError, build_selection, profession_menu_text


class WebCreatorValidationError(ValueError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field
        self.message = message


@dataclass(frozen=True, slots=True)
class CreatorChoicePayload:
    value: str
    label: str
    description: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload: dict[str, str] = {"value": self.value, "label": self.label}
        if self.description is not None:
            payload["description"] = self.description
        return payload


@dataclass(frozen=True, slots=True)
class CreatorStepPayload:
    step_id: str
    title: str
    prompt: str
    input_type: str
    choices: list[CreatorChoicePayload]
    back_available: bool
    cancel_available: bool

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "step_id": self.step_id,
            "title": self.title,
            "prompt": self.prompt,
            "input_type": self.input_type,
            "back_available": self.back_available,
            "cancel_available": self.cancel_available,
        }
        if self.choices:
            payload["choices"] = [choice.to_dict() for choice in self.choices]
        return payload


def _choice(value: str, label: str, description: str | None = None) -> CreatorChoicePayload:
    return CreatorChoicePayload(value=value, label=label, description=description)


def _definition_choices(definitions: dict[str, Any]) -> list[CreatorChoicePayload]:
    return [_choice(defn.key, defn.label, getattr(defn, "description", None) or None) for defn in definitions.values()]


def _profession_choices(definitions: dict[str, Any]) -> list[CreatorChoicePayload]:
    return [_choice(defn.key, defn.label, defn.description) for defn in definitions.values()]


def _secondary_profession_choices() -> list[CreatorChoicePayload]:
    return [_choice("brak", "brak", "Nie wybierasz profesji dodatkowej."), *_profession_choices(ADDITIONAL_PROFESSIONS)]


class WebCreatorFlow:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self._step_index = 0
        self._answers: dict[str, str | int] = {}
        self._cancelled = False
        self._finished = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    @property
    def finished(self) -> bool:
        return self._finished

    def current_step(self) -> CreatorStepPayload:
        return self._steps()[self._step_index]

    def current_step_dict(self) -> dict[str, Any]:
        return self.current_step().to_dict()

    def start_payload(self) -> dict[str, Any]:
        return {"username": self.username, "step": self.current_step_dict()}

    def submit(self, step_id: str, value: str) -> CharacterCreationProfile | None:
        step = self.current_step()
        if step.step_id != step_id:
            raise WebCreatorValidationError("step_id", "Kreator jest na innym kroku.")
        self._store_answer(step.step_id, value)
        if self._step_index >= len(self._steps()) - 1:
            return self._build_profile()
        self._step_index += 1
        return None

    def mark_finished(self) -> None:
        self._finished = True

    def back(self, step_id: str) -> CreatorStepPayload:
        step = self.current_step()
        if step.step_id != step_id:
            raise WebCreatorValidationError("step_id", "Kreator jest na innym kroku.")
        if self._step_index == 0:
            raise WebCreatorValidationError("step_id", "Nie można cofnąć się z pierwszego kroku.")
        self._step_index -= 1
        return self.current_step()

    def cancel(self, step_id: str) -> None:
        step = self.current_step()
        if step.step_id != step_id:
            raise WebCreatorValidationError("step_id", "Kreator jest na innym kroku.")
        self._cancelled = True

    def _steps(self) -> list[CreatorStepPayload]:
        steps: list[CreatorStepPayload] = [
            CreatorStepPayload("name", "Imię", "— Jak cię zwać?", "text", [], False, True),
            CreatorStepPayload(
                "gender_id",
                "Płeć",
                gender_step().prompt,
                "choice",
                [_choice(option.key, option.label, option.description) for option in gender_step().options],
                True,
                True,
            ),
            CreatorStepPayload("age", "Wiek", "— Ile masz lat?", "number", [], True, True),
            CreatorStepPayload("origin", "Pochodzenie", origin_prompt_text(), "choice", _definition_choices(ORIGIN_DEFINITIONS), True, True),
            CreatorStepPayload("childhood", "Dzieciństwo", childhood_prompt_text(), "choice", _definition_choices(CHILDHOOD_DEFINITIONS), True, True),
            CreatorStepPayload("birth_region", "Region urodzenia", birth_region_prompt_text(), "choice", _definition_choices(BIRTH_REGION_DEFINITIONS), True, True),
            CreatorStepPayload("main_profession", "Profesja główna", profession_menu_text(), "choice", _profession_choices(MAIN_PROFESSIONS), True, True),
            CreatorStepPayload("secondary_profession", "Profesja dodatkowa", profession_menu_text(), "choice", _secondary_profession_choices(), True, True),
        ]
        gender_id = normalize_gender_id(self._answers.get("gender_id"))
        if gender_id in {"m", "f"}:
            for step in appearance_steps_for_gender(gender_id):
                steps.append(
                    CreatorStepPayload(
                        step.step_id,
                        step.title,
                        step.prompt,
                        "choice",
                        [_choice(option.key, option.label_for_gender(gender_id), option.description) for option in step.options],
                        True,
                        True,
                    )
                )
        return steps

    def _store_answer(self, step_id: str, raw_value: str) -> None:
        value = raw_value.strip()
        try:
            if step_id == "name":
                self._answers["name"] = validate_text("Imię", value, min_length=2, max_length=32)
                return
            if step_id == "gender_id":
                gender = gender_step().resolver(value).key
                if self._answers.get("gender_id") != gender:
                    for key in ("build", "height", "eyes", "hair_color", "hair_style", "beard", "special_feature"):
                        self._answers.pop(key, None)
                self._answers["gender_id"] = gender
                return
            if step_id == "age":
                self._answers["age"] = validate_age(value)
                return
            if step_id == "origin":
                self._answers["origin"] = resolve_origin(value).key
                return
            if step_id == "childhood":
                self._answers["childhood"] = resolve_childhood(value).key
                return
            if step_id == "birth_region":
                self._answers["birth_region"] = resolve_birth_region(value).label
                return
            if step_id == "main_profession":
                self._answers["main_profession"] = build_selection(value).main_profession
                return
            if step_id == "secondary_profession":
                if not value or value.lower() in {"brak", "none", "0"}:
                    self._answers["secondary_profession"] = ""
                    return
                self._answers["secondary_profession"] = build_selection(self._get_required_answer("main_profession"), value).secondary_profession
                return
            if step_id in {step.step_id for step in appearance_steps_for_gender(self._get_required_answer("gender_id"))}:
                step = next(step for step in appearance_steps_for_gender(self._get_required_answer("gender_id")) if step.step_id == step_id)
                self._answers[step_id] = step.resolver(value).key
                return
        except (CharacterCreationError, ProfessionError, ValueError) as exc:
            raise WebCreatorValidationError(step_id, str(exc)) from exc
        raise WebCreatorValidationError(step_id, "Nieznany krok kreatora.")

    def _get_required_answer(self, key: str) -> str:
        value = self._answers.get(key)
        if not isinstance(value, str) or not value:
            raise WebCreatorValidationError(key, "Najpierw uzupełnij poprzedni krok.")
        return value

    def _build_profile(self) -> CharacterCreationProfile:
        secondary_profession = self._answers.get("secondary_profession")
        beard_answer = self._answers.get("beard")
        beard_value = beard_answer if isinstance(beard_answer, str) and beard_answer else "brak"
        return CharacterCreationProfile.build(
            name=self._get_required_answer("name"),
            gender_id=self._get_required_answer("gender_id"),
            age=self._answers.get("age", 0),
            origin=self._get_required_answer("origin"),
            childhood=self._get_required_answer("childhood"),
            birth_region=self._get_required_answer("birth_region"),
            main_profession=self._get_required_answer("main_profession"),
            secondary_profession=secondary_profession if isinstance(secondary_profession, str) and secondary_profession else None,
            appearance_profile=appearance_profile_from_choices(
                gender_id=self._get_required_answer("gender_id"),
                build=self._get_required_answer("build"),
                height=self._get_required_answer("height"),
                eyes=self._get_required_answer("eyes"),
                hair_color=self._get_required_answer("hair_color"),
                hair_style=self._get_required_answer("hair_style"),
                beard=beard_value,
                special_feature=self._get_required_answer("special_feature"),
            ),
        )
