---
sidebar_position: 3
sidebar_label: "C3. Property"
description: "메서드를 속성처럼 읽게 하는 property를 쓰는 네 가지 경우입니다."
---

# Property

메서드를 속성처럼 읽게 하는 property를 쓰는 네 가지 경우입니다.

## 개념

property(`@property`)를 붙인 메서드는 괄호 없이 속성처럼 읽힙니다. `obj.size()` 대신 `obj.size`로 씁니다.

## 사용 방법

1. **파생 값**: 다른 필드에서 계산되는 값은 저장하지 않고 읽을 때 계산합니다.
2. **지연 로드**: 처음 읽을 때 무거운 데이터를 불러옵니다.
3. **추상 속성**: 하위 클래스가 반드시 제공해야 하는 "값"은 `@property`를 바깥, `@abstractmethod`를 안쪽에
   쌓습니다. 순서를 바꾸면 추상 속성으로 인식되지 않습니다.
4. **상태를 확인한 뒤 돌려주는 값**: `with` 블록 안에서만 유효한 객체는 property에서 상태를 확인하고, 블록
   밖이면 값 대신 오류를 냅니다.

## 왜 필요한가

파생 값을 저장하면 원래 필드가 바뀔 때 둘이 어긋날 수 있습니다. property는 늘 원래 필드에서 계산하므로 어긋나지
않습니다.

## 예시

```python
# 예시: property의 네 가지 쓰임
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Judgement:
    causes: tuple[str, ...]

    # 1. 파생 값
    @property
    def failed(self) -> bool:
        return bool(self.causes)


class Index(ABC):
    # 3. 추상 속성: property가 바깥, abstractmethod가 안쪽입니다
    @property
    @abstractmethod
    def size(self) -> int: ...


class FileIndex(Index):
    def __init__(self, rows: list[str]) -> None:
        self._source = rows
        self._loaded: list[str] | None = None

    # 2. 지연 로드: 처음 읽을 때만 불러옵니다
    @property
    def rows(self) -> list[str]:
        if self._loaded is None:
            self._loaded = list(self._source)
        return self._loaded

    @property
    def size(self) -> int:
        return len(self.rows)


class Snapshot:
    def __init__(self, values: list[int]) -> None:
        self._values = values
        self._open = False

    def __enter__(self) -> "Snapshot":
        self._open = True
        return self

    def __exit__(self, *exc_info: object) -> None:
        self._open = False

    # 4. 상태 확인: with 블록 밖에서는 값을 주지 않습니다
    @property
    def values(self) -> list[int]:
        if not self._open:
            raise RuntimeError("snapshot is closed; use it inside a with block")
        return self._values


print(Judgement(("too short",)).failed, FileIndex(["a", "b"]).size)  # True 2
with Snapshot([1, 2]) as snapshot:
    print(snapshot.values)  # [1, 2]
try:
    snapshot.values
except RuntimeError as error:
    print(error)
```

## Self-Index에서의 사용

| 쓰임 | 위치 |
|---|---|
| 파생 값 | `shortfall`(`pipeline/optimizer.py:134`), `ProposedKey.is_new`, `RevisionDecision.replacement`, `NDCGMetric.label` |
| 지연 로드 | `QwenEmbBackend.lookup`(`adapters/browsecomp/adapters/embedding.py:61`), `Endpoint.model`(`endpoints.py:53`. 모델 이름이 비어 있을 때만 서버에 물어봅니다) |
| 추상 속성 | `index/contracts.py:72`, `encoding/contracts.py:20`, `runtime/workflows/execution.py:105` |
| 상태 확인 | snapshot의 모든 속성이 `self._active()`를 거칩니다(`retrieval/snapshots.py:81`) |

## 주의할 점

property는 속성 읽기처럼 보이기 때문에, 네트워크 호출처럼 느리거나 실패할 수 있는 동작을 숨기면 호출하는 쪽이
비용을 예상하지 못합니다. `Endpoint.model`이 이 경계에 있습니다. cache([C8](c8-cache.md))로 조회 결과를 재사용하지만, 처음
읽을 때는 네트워크 요청이 발생합니다.
