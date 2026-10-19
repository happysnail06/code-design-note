---
sidebar_position: 2
sidebar_label: "C2. NamedTuple"
description: "풀어서 받는 작은 반환값과 JSON으로 내보낼 작은 레코드를 만드는 방법입니다."
---

# NamedTuple

풀어서 받는 작은 반환값과 JSON으로 내보낼 작은 레코드를 만드는 방법입니다.

## 개념

NamedTuple은 필드 이름이 붙은 tuple입니다. 위치로 풀어서 받을 수도 있고 이름으로 읽을 수도 있습니다.
`_asdict()`로 dict가 됩니다.

## 사용 방법

호출하는 쪽이 `ids, scores = ...`처럼 풀어서 받는 반환값은 NamedTuple로 만듭니다.

## 왜 필요한가

일반 tuple을 돌려주면 `result[0]`이 무엇인지 알 수 없지만, NamedTuple은 `result.ids`로 읽을 수 있습니다. 풀어서
받는 기존 코드도 그대로 동작합니다.

## 예시

```python
# 예시: 이름으로도, 위치로도 읽을 수 있는 반환값
import json
from typing import NamedTuple


class SearchResult(NamedTuple):
    ids: list[int]
    scores: list[float]


def search() -> SearchResult:
    return SearchResult([3, 1], [0.9, 0.4])


ids, scores = search()
print(search().scores)  # [0.9, 0.4]
print(json.dumps(search()._asdict()))  # {"ids": [3, 1], "scores": [0.9, 0.4]}
```

## Self-Index에서의 사용

`KeySearchResult(key_ids, scores)`(`retrieval/snapshots.py:16`), `StepSpec`(`runtime/plan.py:5`),
`ExecutionPlan.to_dict()`의 `s._asdict()`(`plan.py:18`).

## 주의할 점

생성할 때 검사가 필요하거나 필드가 늘어날 값은 frozen dataclass로 만듭니다. NamedTuple에는 `__post_init__`이
없습니다.
