---
sidebar_position: 7
sidebar_label: "B7. Context와 상태 객체"
description: "단계 사이에 넘기는 값 묶음에서 입력과, 실행 중 바뀌는 상태를 나눠 담는 방법입니다."
---

# Context와 상태 객체

단계 사이에 넘기는 값 묶음에서 입력과, 실행 중 바뀌는 상태를 나눠 담는 방법입니다.

## 개념

context는 여러 단계가 함께 쓰는 값을 묶어 단계에서 단계로 넘기는 객체입니다.

## 사용 방법

- `Context`에는 입력 데이터(texts), 함께 사용하는 객체(llm, index, retriever), 단계별 상태 객체를 구분해 담습니다.
  같은 객체를 계속 참조해도 index의 내부 데이터는 실행 중 바뀔 수 있습니다.
- 상태 객체는 `RoundState`, `QueryState`, `SelectionState`처럼 관심사별로 작게 나눕니다.
- 큰 상태는 `repr=False`로 두어 디버그 출력이 길어지지 않게 합니다.

## 왜 필요한가

상태를 역할별 객체로 나누면 각 단계가 변경하는 값을 확인하기 쉽습니다. 입력 데이터, 공용 객체, 단계별 상태를
구분하면 변경이 영향을 주는 범위도 파악하기 쉽습니다.

## 예시

```python
# 예시: 입력과 바뀌는 상태를 나눠 담은 context
from dataclasses import dataclass, field


@dataclass
class RoundState:
    round: int = 0
    added: int = 0


@dataclass
class Context:
    texts: list[str]
    round_state: RoundState = field(default_factory=RoundState)
    cache: dict[str, int] = field(default_factory=dict, repr=False)


context = Context(["a", "b"])
context.round_state.round += 1
print(context)  # Context(texts=['a', 'b'], round_state=RoundState(round=1, added=0))
```

## Self-Index에서의 사용

`src/selfindex/pipeline/contracts.py:55`

```python
@dataclass
class Context:
    texts: list
    encode: TextEncoding
    llm: GenerationClient
    ...
    round_state: RoundState = field(default_factory=RoundState)
    query_state: QueryState = field(default_factory=QueryState, repr=False)
    selection_state: SelectionState = field(default_factory=SelectionState, repr=False)
```

## 주의할 점

이 레포에서도 `_units()`가 `ctx.selection_state.units`에 계산 결과를 저장하는 것처럼, 상태 객체가 캐시 역할까지
맡는 곳이 있습니다. 어떤 함수가 어떤 상태를 바꾸는지는 이름이나 docstring으로 드러내야 합니다.
