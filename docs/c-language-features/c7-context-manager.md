---
sidebar_position: 7
sidebar_label: "C7. Context manager"
description: "한 함수 안에서 상태를 바꾸고 복원할 때는 `@contextmanager`, 객체의 자원 사용과 정리를 관리할 때는 `__enter__`/`__exit__`를 쓰는 방법입니다."
---

# Context manager

한 함수 안에서 상태를 바꾸고 복원할 때는 `@contextmanager`, 객체의 자원 사용과 정리를 관리할 때는
`__enter__`/`__exit__`를 쓰는 방법입니다.

## 개념

- **context manager**는 `with` 블록에 들어갈 때 준비하고, 나올 때 정리하는 객체입니다. 블록 안에서 예외가 나도
  정리는 실행됩니다.
- **contextmanager**(`@contextlib.contextmanager`)는 `yield`가 하나 있는 함수로 context manager를 만들게 해
  줍니다.
- **ExitStack**은 정리할 일을 여러 개 등록해 두었다가 역순으로 실행해 주는 표준 도구입니다.

## 사용 방법

- "바꾸고, 블록을 실행하고, 되돌린다"가 한 함수로 끝나면 `@contextmanager`를 씁니다. 되돌리는 코드는 `yield`
  뒤의 `finally`에 둡니다.
- 객체가 자원을 사용하는 동안 여러 메서드에서 그 자원에 접근해야 하면 `__enter__`/`__exit__`를
  구현합니다.
- `__enter__`가 중간에 실패하면 그때까지 잡은 자원을 역순으로 풀고 예외를 다시 올립니다.

## 왜 필요한가

정리 코드가 `finally`나 `__exit__`에 있으면 예외가 나도, 중간에 `return`해도 정리를 빠뜨리지 않습니다.

## 예시

외부 객체의 속성을 잠시 바꿨다가 되돌리는 context manager입니다. 원래 없던 속성은 sentinel로 구분해서 되돌릴 때
삭제합니다.

```python
# 예시: 여러 속성을 잠시 바꾸고, 블록이 끝나면 모두 되돌립니다
from contextlib import ExitStack, contextmanager
from types import SimpleNamespace
from collections.abc import Iterator

_MISSING = object()


@contextmanager
def patched(target: object, **values: object) -> Iterator[None]:
    with ExitStack() as stack:
        for name, value in values.items():
            # 원래 값을 기억하고, 되돌리는 일을 먼저 등록한 뒤에 바꿉니다
            original = getattr(target, name, _MISSING)
            stack.callback(_restore, target, name, original)
            setattr(target, name, value)
        yield


def _restore(target: object, name: str, original: object) -> None:
    # 원래 없던 속성은 삭제해서 되돌립니다
    if original is _MISSING:
        delattr(target, name)
    else:
        setattr(target, name, original)


config = SimpleNamespace(timeout=10)
try:
    with patched(config, timeout=1, retries=0):
        print(config.timeout, config.retries)  # 1 0
        raise RuntimeError("블록 안에서 실패해도")
except RuntimeError:
    pass
print(vars(config))  # {'timeout': 10} — 되돌아갔고, retries는 지워졌습니다
```

## Self-Index에서의 사용

| 이름 | 위치 | 하는 일 |
|---|---|---|
| `patched_attributes` | `adapters/browsecomp/adapters/compatibility.py:7` | 위 예시와 같은 구조로 속성을 바꾸고 되돌립니다 |
| `_publication_lock` | `adapters/browsecomp/pipeline/build_bm25_index.py:49` | 기다리지 않는 파일 lock을 잡고, 이미 잡혀 있으면 `FileExistsError`로 바꿔 올립니다([D4](../d-failure-handling/d4-nonblocking-lock.md)) |
| `SnapshotLock.readonly`, `mutation` | `index/contracts.py:21` | thread별 읽기 lease 수를 세고, 다 읽으면 기다리던 쓰기를 깨웁니다 |
| `IndexSnapshot.__enter__` | `retrieval/snapshots.py:38` | lease를 잡고 view를 만들고, 실패하면 잡은 것을 역순으로 풀고 다시 올립니다 |

여기서 **read lease**는 snapshot을 사용하는 동안 index 변경을 제한하는 장치입니다.
`SnapshotLock.mutation()`은 다른 thread의 read lease가 끝날 때까지 기다리고, read lease를 가진 thread가
직접 변경을 시도하면 오류를 냅니다(`index/contracts.py:36`). 이 snapshot은 index 전체를 복사하는 방식이 아니라,
조회하는 동안 변경을 막아 일관된 상태를 유지합니다. `OptimizerLoop`는 snapshot에서 수정안을 계산한 뒤,
lease를 해제하고 index에 반영합니다(`pipeline/engine.py:77`, `:94`).

```python
@contextmanager
def readonly(self):
    thread = threading.get_ident()
    with self:
        self._leases[thread] = self._leases.get(thread, 0) + 1
    try:
        yield
    finally:
        with self:
            self._leases[thread] -= 1
            if not self._leases[thread]:
                del self._leases[thread]
            self._released.notify_all()
```
