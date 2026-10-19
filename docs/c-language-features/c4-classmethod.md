---
sidebar_position: 4
sidebar_label: "C4. Classmethod"
description: "클래스를 첫 인자로 받는 classmethod를 쓰는 세 가지 경우입니다."
---

# Classmethod

클래스를 첫 인자로 받는 classmethod를 쓰는 세 가지 경우입니다.

## 개념

classmethod(`@classmethod`)는 객체 대신 클래스를 첫 인자 `cls`로 받습니다. 객체를 만들지 않고
`ClassName.method()`로 부를 수 있고, 하위 클래스에서 부르면 `cls`가 그 하위 클래스가 됩니다.

## 사용 방법

1. **이름 있는 생성자**: 객체를 만드는 경로마다 이름을 붙입니다. `from_env()`, `of(name)`, `load(directory)`.
2. **객체 없이 하는 검사**: class attribute만 보고 입력을 검사합니다. 무거운 객체를 만들기 전에 잘못된 입력을
   거부할 수 있습니다.
3. **역할별 등록 decorator**: 기본 클래스에 `register`를 classmethod로 두고, 하위 클래스마다 자기 표를 따로
   둡니다. 그러면 `@A.register(...)`와 `@B.register(...)`가 서로 다른 표에 등록합니다.

## 예시

```python
# 예시: 이름 있는 생성자, 객체 없이 하는 검사, 역할별 등록
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    rounds: int

    # 1. 환경 변수에서 만드는 생성자
    @classmethod
    def from_env(cls) -> "Settings":
        return cls(int(os.environ.get("ROUNDS", "3")))


class Factory:
    tasks = ("encode", "search")

    # 2. 객체를 만들지 않고 class attribute만 보고 검사합니다
    @classmethod
    def validate_task(cls, task: str) -> None:
        if task not in cls.tasks:
            raise ValueError(f"{cls.__name__} supports {cls.tasks}, not {task!r}")


class Backbone:
    def __init__(self, model: str) -> None:
        self.model = model

    # 3. 하위 클래스마다 자기 backbones 표에 등록합니다
    @classmethod
    def register(cls, *models: str):
        def register(backbone: type) -> type:
            cls.backbones.update(dict.fromkeys(models, backbone))
            return backbone

        return register

    @classmethod
    def for_model(cls, model: str) -> "Backbone":
        # 등록되지 않은 모델이면 그 역할의 기본 클래스를 씁니다
        return cls.backbones.get(model, cls)(model)


class AgentBackbone(Backbone):
    backbones: dict[str, type] = {}


class JudgeBackbone(Backbone):
    backbones: dict[str, type] = {}


@AgentBackbone.register("kimi-k2.5")
class KimiAgent(AgentBackbone):
    pass


print(Settings.from_env())
Factory.validate_task("encode")
print(type(AgentBackbone.for_model("kimi-k2.5")).__name__)  # KimiAgent
print(type(JudgeBackbone.for_model("kimi-k2.5")).__name__)  # JudgeBackbone — 다른 표입니다
```

## Self-Index에서의 사용

- 이름 있는 생성자: `of()`(`runtime/platform/settings.py:24`). 덮어쓸 수 있는 필드를 `CORPUS_SETTINGS`로 제한하고
  `dataclasses.replace`로 새 객체를 만듭니다.
- 객체 없이 하는 검사: `Runner`의 `FACTORIES[family].validate_task(task)`(`runtime/runner.py:34`).
- 역할별 등록: `Backbone.register`와 `for_model`(`llm/backbones.py:14`).

```python
@classmethod
def of(cls, name, **corpus_settings):
    if name not in ENCODERS:
        raise ValueError(f"unknown encoder {name} (choose from {list(ENCODERS)})")
    if unknown := sorted(set(corpus_settings) - set(CORPUS_SETTINGS)):
        raise ValueError(f"a corpus cannot set the encoder's {unknown}")
    ...
    return replace(table, **corpus_settings)
```

## 주의할 점

이 레포의 기본 클래스 `Backbone`에는 `backbones`가 없으므로 `Backbone.register(...)`를 부르면 `AttributeError`가
납니다. 이 방식을 쓸 때는 기본 클래스에서 부르는 경우를 막거나, 이유를 밝히는 오류를 직접 냅니다.
