---
sidebar_position: 2
sidebar_label: "A2. Lazy import"
description: "일부 기능에서만 필요한 모듈은 그 기능을 실행하는 함수 안에서 import해서, 그 모듈이 없는 환경에서도 나머지 기능이 돌게 하는 방법입니다."
---

# Lazy import

일부 기능에서만 필요한 모듈은 그 기능을 실행하는 함수 안에서 import해서, 그 모듈이 없는 환경에서도 나머지
기능이 돌게 하는 방법입니다.

## 개념

lazy import는 파일 첫머리가 아니라 함수 안에서 하는 import입니다. 그 함수를 부를 때에야 import되므로, 그
함수를 쓰지 않는 실행에서는 해당 모듈이 설치되어 있지 않아도 됩니다.

## 사용 방법

- adapter([A1](a1-adapter-upstream.md))는 핵심 패키지(`selfindex`)를 파일 첫머리에서 자유롭게 import합니다.
- 핵심 패키지는 adapter를 파일 첫머리에서 import하지 않습니다. adapter가 필요한 메서드 안에서만 import합니다.
- torch, pyserini처럼 무겁거나 설치가 선택인 라이브러리도 실제로 쓰는 함수 안에서만 import합니다. 이 레포에는
  이런 import가 146곳 있습니다.

## 왜 필요한가

framework만 설치한 환경에서도 `python run.py list`와 retrieval 실험이 돌아갑니다. 무거운 라이브러리를 import하는
시간도 그 기능을 쓰는 실행에만 듭니다.

## 예시

```python
# 예시: 무거운 라이브러리는 그것이 필요한 함수 안에서만 import합니다
def keyword_score(query: str, doc: str) -> int:
    # 표준 기능만 쓰므로 어떤 환경에서도 동작합니다
    return sum(word in doc.split() for word in query.split())


def dense_score(query: str, doc: str) -> float:
    # torch는 이 함수를 부를 때만 필요하므로 여기서 import합니다
    import torch

    ...


# torch가 설치되지 않은 환경에서도 이 줄은 실행됩니다
print(keyword_score("red apple", "an apple a day"))  # 1
```

## Self-Index에서의 사용

`src/selfindex/runtime/catalog/benchmarks.py:121`

```python
@staticmethod
def _search_adapter(spec):
    from browsecomp.adapters.search_factory import search_adapter_name
    from selfindex.runtime.catalog.retrievers import RETRIEVERS
    ...
```

## 주의할 점

lazy import는 "모듈이 없다"는 오류를 실행 도중으로 미룹니다. 프로그램 전체가 그 라이브러리 없이 돌 수 없다면
파일 첫머리에서 import해서, 시작하자마자 실패하게 둡니다.
