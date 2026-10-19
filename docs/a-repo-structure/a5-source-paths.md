---
sidebar_position: 5
sidebar_label: "A5. 소스 파일 기준 경로"
description: "경로를 작업 디렉터리가 아니라 소스 파일 위치에서 계산해서, 어디서 실행해도 같은 파일을 가리키게 하는 방법입니다."
---

# 소스 파일 기준 경로

경로를 작업 디렉터리가 아니라 소스 파일 위치에서 계산해서, 어디서 실행해도 같은 파일을 가리키게 하는
방법입니다.

## 개념

`Path(__file__)`은 지금 실행 중인 소스 파일의 경로입니다. `.parents[N]`은 그 파일에서 N+1단계 위의
디렉터리입니다.

## 사용 방법

- 모든 경로 상수는 `Path(__file__).resolve().parents[N]`에서 출발합니다.
- upstream 코드를 `sys.path`에 올리는 일은 `_bootstrap.py` 한 파일만 합니다.

## 왜 필요한가

어느 디렉터리에서 실행하든 같은 파일을 가리킵니다. import 경로를 바꾸는 코드가 한 곳에만 있으므로, import
문제가 생기면 그 파일만 보면 됩니다.

## 예시

```python
# 예시: 작업 디렉터리 대신 소스 파일 위치에서 경로를 계산합니다
from pathlib import Path

# 이 파일이 <repo>/src/tool/paths.py라면 parents[2]는 <repo>입니다
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
print(DATA_DIR.name)  # data
```

## Self-Index에서의 사용

`src/selfindex/runtime/platform/environment.py:7`, `adapters/browsecomp/agent/_bootstrap.py`

```python
REPO_ROOT = str(Path(__file__).resolve().parents[4])
IMPORT_ROOTS = (os.path.join(REPO_ROOT, "src"), ADAPTERS_ROOT)
```
