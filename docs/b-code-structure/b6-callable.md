---
sidebar_position: 6
sidebar_label: "B6. Callable"
description: "실행할 동작을 함수, lambda, 호출 가능한 객체로 전달받는 방법입니다."
---

# Callable

실행할 동작을 함수, lambda, 호출 가능한 객체로 전달받는 방법입니다.

## 개념

- **Callable**은 괄호를 붙여 부를 수 있는 모든 것을 뜻하는 타입입니다.
- **`__call__`**을 정의한 객체는 함수처럼 `obj()`로 부를 수 있습니다.

## 사용 방법

- 실행 단위를 `Callable[[], int | None]`로 받습니다. lambda, 일반 함수, `__call__`을 가진 객체를 모두
  인자로 전달할 수 있습니다.
- 실행에 필요한 값(명령, 인자, 환경)을 들고 있어야 하면 `__call__`을 가진 frozen dataclass로 만듭니다.

## 왜 필요한가

단계를 실행하는 쪽은 "부르면 exit code가 나온다"만 알면 됩니다. 단계가 함수인지 하위 프로세스인지 몰라도
됩니다.

## 예시

```python
# 예시: lambda와 __call__ 객체를 같은 Stage에 넣습니다
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    name: str
    action: Callable[[], int]


@dataclass(frozen=True)
class Command:
    """하위 프로세스 하나를 들고 있다가, 부르면 실행하고 exit code를 돌려줍니다."""

    arguments: tuple[str, ...]

    def __call__(self) -> int:
        return subprocess.run(self.arguments, check=False).returncode


stages = [
    Stage("inline", lambda: 0),
    Stage("process", Command((sys.executable, "-c", "pass"))),
]
for stage in stages:
    print(stage.name, stage.action())  # inline 0, process 0
```

## Self-Index에서의 사용

`src/selfindex/runtime/workflows/execution.py:13`

```python
@dataclass(frozen=True)
class Stage:
    name: str
    action: Callable[[], int | None]
    artifacts: Callable[[], tuple[Path, ...]] | None = None

@dataclass(frozen=True)
class Command:
    name: str
    arguments: tuple[str, ...]
    environment: Mapping[str, str]
    directory: Path

    def __call__(self) -> int:
        ...
```

같은 방식으로 `EncodedTexts`(`validation/base.py:15`)는 미리 encode한 결과를 들고 있다가 함수처럼 조회되고,
`TextEncoding` Protocol(`pipeline/contracts.py:15`)은 `__call__` 시그니처만으로 encoder의 약속을 정합니다.
