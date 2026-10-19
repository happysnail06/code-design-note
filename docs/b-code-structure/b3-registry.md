---
sidebar_position: 3
sidebar_label: "B3. Registry"
description: "구현을 이름으로 등록하고 이름으로 꺼내 쓰는 방법입니다. 등록할 때 이름 중복과 추상 클래스를 거부합니다."
---

# Registry

구현을 이름으로 등록하고 이름으로 꺼내 쓰는 방법입니다. 등록할 때 이름 중복과 추상 클래스를 거부합니다.

## 개념

registry는 이름을 키로 구현을 등록해 두고, 실행할 때 이름(예: CLI 인자 `--retriever bm25`)으로 꺼내 쓰는
표입니다. 새 구현을 추가할 때 `if name == "bm25": ... elif ...` 분기를 늘리지 않아도 됩니다.

## 사용 방법

등록하는 방식은 네 가지가 있습니다.

| 방식 | 언제 쓰나 |
|---|---|
| `Registry` 객체와 `register_*()` 함수 | 객체나 설정을 이름으로 등록하고, 등록할 때 타입, 중복, 이름 형식을 검사해야 할 때 |
| class decorator (`@Base.register("name")`) | 클래스 하나를 여러 키에 묶을 때. 클래스 정의 바로 위에 등록 키가 보입니다 |
| `__init_subclass__` ([C9](../c-language-features/c9-init-subclass.md)) | 하위 클래스를 정의하기만 하면 등록되어야 할 때 |
| 문자열 명령 표 ([A3](../a-repo-structure/a3-entry-point.md)) | import 비용이 큰 대상을 실행 직전에만 불러와야 할 때 |

어떤 방식이든 다음을 지킵니다.

- 조회에 실패하면 무엇이 없는지와 무엇을 쓸 수 있는지를 함께 알립니다.
- 등록 대상이 구체 클래스인지 `inspect.isabstract()`로 확인합니다.
- 여러 개를 한 번에 등록할 때는 전부 검증한 뒤에 등록합니다.
- argparse의 `choices`를 registry에서 만들어서, 등록하면 CLI 선택지도 함께 늘어나게 합니다.

## 왜 필요한가

구현을 추가하는 일이 "클래스를 만들고 등록한다"로 끝납니다. 실행 코드의 분기, CLI 선택지, 오류 메시지를
따로 고치지 않아도 됩니다.

## 예시

검증하는 registry와 class decorator 등록입니다. `Mapping`은 C10에서 설명합니다.

```python
# 예시: 등록할 때 검증하고, 조회에 실패하면 선택지를 알려 주는 registry
import inspect
from collections.abc import Iterator, Mapping


class Registry(Mapping):
    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._items: dict[str, type] = {}

    def register(self, name: str, item: type) -> None:
        # 빈 이름, 중복 이름, 추상 클래스는 등록 시점에 거부합니다
        if not name:
            raise ValueError(f"{self._kind} name must not be empty")
        if name in self._items:
            raise ValueError(f"{self._kind} {name!r} is already registered")
        if inspect.isabstract(item):
            raise TypeError(f"{self._kind} {name!r} must be a concrete class")
        self._items[name] = item

    def __getitem__(self, name: str) -> type:
        # 없는 이름이면 쓸 수 있는 이름을 함께 알립니다
        if name not in self._items:
            raise KeyError(f"unknown {self._kind}: {name}; available: {', '.join(sorted(self._items))}")
        return self._items[name]

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)


RETRIEVERS = Registry("retriever")


def retriever(name: str):
    """클래스 정의 위에 붙여 RETRIEVERS에 등록하는 class decorator입니다."""

    def register(cls: type) -> type:
        RETRIEVERS.register(name, cls)
        return cls

    return register


@retriever("bm25")
class BM25:
    pass


print(sorted(RETRIEVERS))  # ['bm25'] — argparse choices로 그대로 씁니다
try:
    RETRIEVERS["dense"]
except KeyError as error:
    print(error)  # 'unknown retriever: dense; available: bm25'
try:
    RETRIEVERS.register("bm25", BM25)
except ValueError as error:
    print(error)  # retriever 'bm25' is already registered
```

## Self-Index에서의 사용

| 방식 | 위치 |
|---|---|
| `Registry` 객체와 `register_*()` 함수 | `runtime/registry.py`, `register_benchmark`, `register_retriever`, `register_factory`, `register_search_adapter` |
| class decorator | `@AgentBackbone.register(model)`, `llm/backbones.py:14` |
| `__init_subclass__` | `adapters/browsecomp/agent/backbones.py:45` |
| 문자열 명령 표 | `COMMANDS`, `runtime/commands.py:10` |

- 조회 실패 메시지: `f"unknown retriever backend: {name}; available: {', '.join(BACKENDS)}"`.
- `inspect.isabstract()` 검사: `runtime/factories.py:160`, `runtime/catalog/benchmarks.py:264`.
- 전부 검증한 뒤 등록: `register_domains`, `benchmarks.py:260`.
- registry에서 만든 CLI 선택지: `choices=list(SEARCH_ADAPTERS)`, `choices=sorted(RETRIEVERS)`.
