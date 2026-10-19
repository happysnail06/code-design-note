---
sidebar_position: 1
sidebar_label: "D1. Atomic replace"
description: "임시 파일에 다 쓴 뒤 한 번에 교체해서, 반쯤 쓴 파일이 남지 않게 하는 방법입니다."
---

# Atomic replace

임시 파일에 다 쓴 뒤 한 번에 교체해서, 반쯤 쓴 파일이 남지 않게 하는 방법입니다.

## 개념

`os.replace(src, dst)`는 같은 파일 시스템 안에서 한 번에 이름을 바꿉니다. 다른 프로세스는 이전 파일이나 완성된
새 파일 중 하나만 보게 되고, 반쯤 쓴 파일은 보지 않습니다.

## 사용 방법

- 쓰기 함수를 인자로 받는 `atomic_replace(path, write)` 하나로 JSON, JSONL, numpy 파일을 모두 처리합니다.
- 임시 파일은 같은 디렉터리에 `.`으로 시작하는 숨김 파일로 만듭니다.
- 실패하면 임시 파일을 지웁니다.

## 왜 필요한가

쓰는 도중 프로세스가 죽어도 이전 산출물이 그대로 남습니다. 다음 실행이 깨진 파일을 읽고 엉뚱한 결과를 내는 일이
없습니다.

## 예시

```python
# 예시: 임시 파일에 다 쓴 뒤 한 번에 바꿔치기합니다
import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import IO


def atomic_replace(path: Path, write: Callable[[IO[str]], None]) -> None:
    # 같은 디렉터리에 숨김 임시 파일을 만들어야 os.replace가 한 번에 바꿀 수 있습니다
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "w") as stream:
            write(stream)
        os.replace(temporary, path)
    except BaseException:
        # 실패하면 임시 파일을 지우고 원래 오류를 그대로 올립니다
        Path(temporary).unlink(missing_ok=True)
        raise


target = Path(tempfile.mkdtemp()) / "result.json"
atomic_replace(target, lambda stream: json.dump({"ndcg": 0.41}, stream))
print(target.read_text())  # {"ndcg": 0.41}
```

## Self-Index에서의 사용

`storage/artifacts.py:25`의 `atomic_replace(path, write)`.
