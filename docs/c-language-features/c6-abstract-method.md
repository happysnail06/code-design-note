---
sidebar_position: 6
sidebar_label: "C6. Abstract method"
description: "모든 구현이 가져야 하는 기능은 abstract method로, 일부 구현만 지원하는 기능은 이유를 밝히는 오류로 두는 방법입니다."
---

# Abstract method

모든 구현이 가져야 하는 기능은 abstract method로, 일부 구현만 지원하는 기능은 이유를 밝히는 오류로 두는
방법입니다.

## 개념

- **abstract method**(`@abstractmethod`)는 하위 클래스가 반드시 구현해야 합니다. 구현하지 않으면 객체를 만들 때
  실패합니다.
- 일반 메서드에서 `raise NotImplementedError`를 하면, 하위 클래스가 구현하지 않아도 객체는 만들어지고 그 메서드를
  부를 때만 실패합니다.

## 사용 방법

- 모든 구현이 가져야 하는 동작만 abstract method로 두고, 본문은 `...` 한 줄로 씁니다.
- 일부 구현만 지원하는 동작은 기본 구현에서 클래스 이름을 넣어 `NotImplementedError`로 실패시킵니다.
- 여러 건을 한 번에 처리하는 메서드는 한 건짜리 메서드를 반복하는 기본 구현을 두고, 더 빠르게 할 수 있는
  구현만 override합니다.

## 왜 필요한가

모든 기능을 abstract method로 두면 그 기능이 필요 없는 구현도 빈 메서드를 억지로 채워야 합니다. 이유를 밝히는
`NotImplementedError`는 "이 구현은 이 기능을 지원하지 않는다"를 부르는 순간 정확히 알려 줍니다.

## 예시

```python
# 예시: 필수 기능, 선택 기능, 일괄 처리 기본 구현
from abc import ABC, abstractmethod


class KeyIndex(ABC):
    # 모든 index가 반드시 가져야 하는 기능입니다
    @abstractmethod
    def add(self, doc: int, key: str) -> None: ...

    # 일부 index만 지원하는 기능입니다
    def replace(self, doc: int, key: str) -> None:
        raise NotImplementedError(f"{type(self).__name__} does not support key replacement")

    # 일괄 버전은 한 건짜리를 반복하는 기본 구현을 둡니다
    def replace_many(self, replacements: dict[int, str]) -> None:
        for doc, key in replacements.items():
            self.replace(doc, key)


class AppendOnlyIndex(KeyIndex):
    def __init__(self) -> None:
        self.keys: list[tuple[int, str]] = []

    def add(self, doc: int, key: str) -> None:
        self.keys.append((doc, key))


index = AppendOnlyIndex()
index.add(1, "apple")
try:
    index.replace_many({1: "pear"})
except NotImplementedError as error:
    print(error)  # AppendOnlyIndex does not support key replacement
```

## Self-Index에서의 사용

`index/contracts.py:98`

```python
def replace_validated(self, doc, texts):
    raise NotImplementedError(
        f"{type(self).__name__} does not support exact validated-key replacement"
    )

def replace_validated_many(self, replacements):
    for doc, keys in replacements.items():
        self.replace_validated(doc, keys)
```

## 주의할 점

abstract method는 하위 클래스로 객체를 만들 때에야 검사됩니다. 클래스를 registry에 넣는 곳에서는
`inspect.isabstract()`로 미리 거부합니다([B3](../b-code-structure/b3-registry.md)).
