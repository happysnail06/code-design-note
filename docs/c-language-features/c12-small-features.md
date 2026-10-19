---
sidebar_position: 12
sidebar_label: "C12. 작은 언어 기능"
description: "자주 쓰이는 작은 Python 기법을 모았습니다."
---

# 작은 언어 기능

자주 쓰이는 작은 Python 기법을 모았습니다.

## 사용 방법

| 기능 | 한 줄 설명 | 예시 | 레포 위치 |
|---|---|---|---|
| walrus `:=` | 값을 변수에 넣으면서 바로 조건에 씁니다 | `if unknown := sorted(set(given) - set(allowed)): raise ValueError(...)` | 37곳 |
| keyword-only argument `*` | `*` 뒤 인자는 이름으로만 넘깁니다. 같은 타입 인자가 여럿일 때 순서 실수를 막습니다 | `def optimize(texts, *, depth, limit)` | `optimize(...)` |
| `zip(strict=True)` | 두 시퀀스의 길이가 다르면 조용히 잘리지 않고 `ValueError`가 납니다 | `for step, task in zip(steps, tasks, strict=True)` | `runner.py:58` 등 |
| `dict.fromkeys(xs)` | 순서를 지키며 중복을 없앱니다. 여러 키에 같은 값을 묶을 때도 씁니다 | `list(dict.fromkeys(["b", "a", "b"]))`는 `['b', 'a']` | `validation/base.py:18` 등 |
| `MappingProxyType` | dict를 읽기 전용으로 보여 줍니다 | `OPTIONS = MappingProxyType({"k": 10})` | `harness_options.py:10`, `workflow.py:25` |
| sentinel `_MISSING = object()` | "값이 없음"과 "`None`이라는 값"을 구분합니다 | `if getattr(obj, name, _MISSING) is _MISSING:` | `compatibility.py:3` |
| `bool` 먼저 거부, 그다음 `operator.index` | `True`가 id 1로 통과하는 일을 막고, 정수로 바꿀 수 있는 값만 받습니다 | `if isinstance(x, bool): raise TypeError(...)` | `index/contracts.py:107`, `revision/base.py:12` |
| `type(code) is not int` | `bool`까지 거부하는 정확한 타입 검사입니다 | `if type(code) is not int: raise TypeError(...)` | `execution.py:77` |
| `raise ... from None` | 원래 예외를 숨깁니다. 원래 예외가 사용자에게 의미 없을 때만 씁니다 | `except BlockingIOError: raise FileExistsError(...) from None` | `build_bm25_index.py:58` |
| `if TYPE_CHECKING:` | 타입 표기에만 필요한 import를 실행 중에는 건너뜁니다 | `if TYPE_CHECKING: from .index import KeyIndex` | `pipeline/contracts.py:7` |
| 괄호로 묶은 여러 context manager | 여러 자원을 한 `with`로 열고, 줄이 길면 괄호로 묶습니다 | `with (open(a) as src, open(b, "w") as dst):` | `build_bm25_index.py:182`, `embedding.py:107` 등 4곳 |
