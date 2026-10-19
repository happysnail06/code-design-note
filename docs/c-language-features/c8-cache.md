---
sidebar_position: 8
sidebar_label: "C8. Cache"
description: "성공한 외부 조회만 기억하게 해서 같은 조회를 한 번만 하는 방법입니다."
---

# Cache

성공한 외부 조회만 기억하게 해서 같은 조회를 한 번만 하는 방법입니다.

## 개념

cache(`@functools.cache`)를 붙이면 같은 인자로 다시 부를 때 함수를 실행하지 않고 저장해 둔 결과를 돌려줍니다.

## 사용 방법

- 예외는 저장되지 않습니다. 조회가 실패하면 다음 호출에서 다시 시도되고, 성공한 결과만 재사용됩니다.
- 캐시 키는 인자 값 그대로입니다. `"http://a/"`와 `"http://a"`는 다른 키이므로, 인자를 먼저 정규화합니다.

## 왜 필요한가

서버에 "어떤 모델을 서빙하는가"를 묻는 조회를 실행마다 한 번만 하게 하면서, 일시적인 실패가 영원히 남지 않게
합니다.

## 예시

```python
# 예시: 실패는 저장되지 않으므로 다음 호출에서 다시 시도됩니다
from functools import cache

calls = []


@cache
def served_model(base_url: str) -> str:
    calls.append(base_url)
    if len(calls) == 1:
        raise ConnectionError("server is starting")
    return "qwen3"


try:
    served_model("http://localhost:8000")
except ConnectionError:
    pass
print(served_model("http://localhost:8000"))  # qwen3 — 두 번째 호출에서 다시 시도했습니다
print(served_model("http://localhost:8000"))  # qwen3 — 이번에는 저장된 값입니다
print(len(calls))  # 2
```

## Self-Index에서의 사용

`src/selfindex/runtime/platform/endpoints.py:17`. URL 끝의 `/`는 `Endpoint.__post_init__`에서 미리 지웁니다([C1](c1-dataclass.md)).

```python
@cache
def served_model_entry(base_url):
    ...
    except (OSError, ValueError) as error:
        raise ValueError(f"cannot list the models served at {base_url}: {error}")
```

## 주의할 점

프로세스가 도는 동안 값이 바뀔 수 있는 대상(서버 재시작으로 모델이 바뀌는 경우 등)에는 기한 없는 캐시가 맞지
않습니다.
