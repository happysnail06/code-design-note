---
sidebar_position: 9
sidebar_label: "C9. __init_subclass__"
description: "하위 클래스를 정의하는 순간 자동으로 등록하는 방법입니다."
---

# `__init_subclass__`

하위 클래스를 정의하는 순간 자동으로 등록하는 방법입니다.

## 개념

기본 클래스에 `__init_subclass__`를 정의하면, 그 클래스를 상속한 하위 클래스가 정의될 때마다 자동으로 불립니다.

## 사용 방법

- `super().__init_subclass__(**kwargs)`를 먼저 부릅니다.
- 등록 조건(예: `name`이 있음)을 둬서 이름 없는 중간 클래스는 등록되지 않게 합니다.
- 이름이 겹치면 정의하는 순간 거부합니다.

## 예시

레포 코드에 없는 이름 중복 검사를 더한 형태입니다.

```python
# 예시: 정의만 하면 등록되고, 이름이 겹치면 정의하는 순간 실패합니다
_AGENTS: dict[str, type] = {}


class Agent:
    name = ""

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # 이름이 없는 중간 클래스는 등록하지 않습니다
        if not cls.name:
            return
        if cls.name in _AGENTS:
            raise ValueError(f"agent {cls.name!r} is already defined by {_AGENTS[cls.name].__name__}")
        _AGENTS[cls.name] = cls


class GptAgent(Agent):
    name = "gpt"


try:
    class AnotherGpt(Agent):
        name = "gpt"
except ValueError as error:
    print(error)  # agent 'gpt' is already defined by GptAgent
print(sorted(_AGENTS))  # ['gpt']
```

## Self-Index에서의 사용

`adapters/browsecomp/agent/backbones.py:45`

```python
def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    if cls.name:
        _REGISTRY[cls.name] = cls
```

## 주의할 점

레포 코드는 이름 중복을 검사하지 않아서, 같은 `name`을 쓴 두 번째 클래스가 첫 번째를 조용히 덮어씁니다. 위
예시처럼 중복을 거부하거나 `Registry.register`([B3](../b-code-structure/b3-registry.md))를 거치게 합니다.
