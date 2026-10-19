---
sidebar_position: 11
sidebar_label: "C11. BaseException"
description: "외부 코드의 `except Exception`에 잡히면 안 되는 신호를 만드는 방법입니다."
---

# BaseException

외부 코드의 `except Exception`에 잡히면 안 되는 신호를 만드는 방법입니다.

## 개념

Python 예외의 뿌리는 `BaseException`이고, 일반 오류는 그 아래의 `Exception`을 상속합니다. `except Exception`은
`Exception` 계열만 잡으므로, `BaseException`을 직접 상속한 예외는 그냥 지나갑니다. `KeyboardInterrupt`가 이렇게
만들어져 있습니다.

## 사용 방법

- 외부 코드의 `except Exception`에 처리되지 않고 호출한 쪽으로 전달되어야 하는 신호만 `BaseException`을 직접
  상속합니다.
- 그 신호를 잡아 처리하는 wrapper를 반드시 함께 둡니다.
- 실패했을 때 상태를 되돌리는 코드도 `except BaseException:`으로 잡고, 되돌린 뒤 반드시 `raise`합니다. 그래야
  `KeyboardInterrupt`로 멈춰도 반쯤 바뀐 상태가 남지 않습니다.

## 왜 필요한가

query별 시간 제한을 외부 라이브러리의 대화 loop 안에서 발생시키면, `Exception`을 상속한 예외는 그 라이브러리가
"도구 호출 실패"로 삼키고 loop를 계속 돕니다. `BaseException`이면 우리 wrapper까지 올라옵니다.

## 예시

```python
# 예시: 외부 loop의 except Exception을 뚫고 올라오는 시간 제한 신호
class Deadline(BaseException):
    pass


def upstream_loop(step) -> None:
    """외부 코드라고 가정합니다. 오류를 잡아 출력하고 계속 돕니다."""
    for turn in range(3):
        try:
            step(turn)
        except Exception as error:
            print("upstream swallowed:", error)


def step(turn: int) -> None:
    if turn == 0:
        raise ValueError("tool failed")
    raise Deadline()


try:
    upstream_loop(step)
except Deadline:
    print("deadline reached")  # ValueError는 삼켜졌지만 Deadline은 올라왔습니다
```

## Self-Index에서의 사용

`adapters/browsecomp/agent/oss_client_ours.py:20`, `:97`

```python
class _QueryDeadline(BaseException): ...

def _conversation_with_deadline(original, client, initial_request, tool_handler, ...):
    _QUERY_CLOCK.started = time.monotonic()
    try:
        out = original(client, initial_request, tool_handler, max_iterations, verbose)
    except _QueryDeadline as deadline:
        ...
        raise
```

상태를 되돌리는 `except BaseException:`은 `index/dense.py:312`, `retrieval/snapshots.py:63`,
`runtime/workflows/execution.py:63`에 있습니다.

## 주의할 점

`BaseException` 상속은 일반 오류 처리를 모두 건너뛰므로, 처리할 wrapper가 정해져 있을 때만 씁니다.
