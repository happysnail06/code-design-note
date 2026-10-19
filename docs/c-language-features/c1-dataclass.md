---
sidebar_position: 1
sidebar_label: "C1. Dataclass"
description: "바뀌지 않는 값은 frozen dataclass로, 바뀌는 상태는 일반 dataclass로 만드는 방법입니다."
---

# Dataclass

바뀌지 않는 값은 frozen dataclass로, 바뀌는 상태는 일반 dataclass로 만드는 방법입니다.

## 개념

- **dataclass**(`@dataclass`)는 필드 선언만으로 `__init__`, `__repr__`, `__eq__`를 만들어 줍니다.
- **frozen dataclass**(`@dataclass(frozen=True)`)는 만든 뒤 필드에 대입할 수 없습니다.
- **`__post_init__`**은 자동 `__init__`이 끝난 직후 불리므로, 검사와 정규화를 여기서 합니다.

## 사용 방법

- 실행 중 바뀌지 않는 값(`Spec`, `Plan`, `Settings`)은 frozen, 바뀌는 상태와 집계(`State`, `Report`)만 일반
  dataclass로 둡니다.
- frozen 객체를 `__post_init__`에서 정규화할 때는 `object.__setattr__`을 씁니다. 일반 대입은 frozen 때문에
  막혀 있기 때문입니다.
- frozen은 필드를 다른 객체로 바꾸는 것만 막고, dict 안의 내용을 바꾸는 것은 막지 않습니다. 그래서 받은 dict는
  복사해서 `MappingProxyType`으로 감쌉니다.
- 타입 표기가 없는 class 변수는 dataclass field가 되지 않고 class attribute로 남습니다. 상수로 쓸 수 있지만,
  값의 변경 자체를 막지는 않습니다.
- list나 dict 같은 기본값은 반드시 `field(default_factory=...)`로 줍니다.

## 왜 필요한가

설정이나 plan의 필드를 실행 도중 실수로 변경하는 일을 막습니다. 필드에 다시 대입하면 즉시 오류가 납니다.

## 예시

```python
# 예시: 생성할 때 검사하고 정규화하며, 받은 dict까지 읽기 전용으로 만듭니다
from dataclasses import FrozenInstanceError, dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class Endpoint:
    base_url: str
    headers: Mapping[str, str] = field(default_factory=dict)
    timeout_env = "HTTP_TIMEOUT_SECONDS"  # 타입 표기가 없으므로 field가 아닌 공유 상수입니다

    def __post_init__(self) -> None:
        # 잘못된 URL은 만드는 순간 거부합니다
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("endpoint must be an absolute HTTP(S) URL")

        # frozen이라 일반 대입이 막혀 있으므로 object.__setattr__으로 정규화합니다
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))
        object.__setattr__(self, "headers", MappingProxyType(dict(self.headers)))


endpoint = Endpoint("http://localhost:8000/", {"x-team": "ir"})
print(endpoint.base_url)  # http://localhost:8000

try:
    endpoint.base_url = "http://other"
except FrozenInstanceError:
    print("필드는 다시 대입할 수 없습니다")

try:
    endpoint.headers["x-team"] = "nlp"
except TypeError:
    print("dict 내용도 바꿀 수 없습니다")
```

## Self-Index에서의 사용

`src/selfindex/runtime/platform/endpoints.py:47`

```python
def __post_init__(self):
    if not isinstance(self.base_url, str) or not isinstance(self.model_name, str):
        raise ValueError("endpoint URL and model must be strings")
    _validate_url(self.base_url)
    object.__setattr__(self, "base_url", self.base_url.rstrip("/"))
```

- dict를 `MappingProxyType(dict(...))`로 감싸는 곳: `adapters/browsecomp/pipeline/workflow.py:25`.
- frozen dataclass로 추상 property를 채우는 곳: `BrowseCompWorkflow`는 `resumed` 필드를 두고 `resume` property가
  그 값을 돌려줍니다. 필드 이름과 property 이름이 같으면 충돌하기 때문입니다(`workflow.py:20`, `:35`).
- 공유 상수: `Endpoint.api_key_env = API_KEY_ENV`(`endpoints.py:45`).
- 기본값을 함수로 계산: `usage: dict = field(default_factory=_empty_usage)`(`or_client_ours.py:73`).

## 주의할 점

이 레포는 `slots=True`, `kw_only=True`를 쓰지 않습니다. 필드가 많은 spec에 `kw_only=True`를 쓰면 위치 인자 순서
실수를 막을 수 있지만, 레포에서 확인된 관행은 아닙니다.
