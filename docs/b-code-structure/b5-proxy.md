---
sidebar_position: 5
sidebar_label: "B5. Proxy"
description: "객체를 감싸서 일부 메서드만 바꾸고, 나머지는 원래 객체에 넘기는 방법입니다."
---

# Proxy

객체를 감싸서 일부 메서드만 바꾸고, 나머지는 원래 객체에 넘기는 방법입니다.

## 개념

- **proxy**는 원래 객체를 속성으로 보관하고, 일부 메서드만 직접 정의하고 나머지는 원래 객체에 넘기는 객체입니다.
- **`__getattr__`**은 객체에 없는 속성을 읽으려 할 때만 불립니다. 그래서 직접 정의하지 않은 속성은 모두
  `__getattr__`을 거쳐 원래 객체로 갑니다.

## 사용 방법

- 바꿀 메서드 한두 개만 직접 정의합니다.
- 나머지 속성 접근은 `__getattr__`으로 원래 객체에 넘깁니다.
- 이미 감싼 객체는 다시 감싸지 않습니다.

## 왜 필요한가

원래 객체가 가진 수십 개의 메서드를 하나하나 옮겨 적지 않아도 됩니다.

## 예시

```python
# 예시: write만 바꾸고 나머지는 원래 stream에 넘기는 proxy
import io


class PrefixWriter:
    def __init__(self, raw: io.TextIOBase) -> None:
        self._raw = raw

    def write(self, text: str) -> int:
        # 내용이 있는 줄에만 prefix를 붙입니다
        return self._raw.write(f"[app] {text}" if text.strip() else text)

    def __getattr__(self, name: str):
        # 직접 정의하지 않은 속성은 모두 원래 stream에서 찾습니다
        return getattr(self._raw, name)


buffer = io.StringIO()
writer = PrefixWriter(buffer)
writer.write("started\n")
print(writer.getvalue())  # [app] started  — getvalue는 __getattr__을 거쳐 StringIO에서 옵니다
```

## Self-Index에서의 사용

`src/selfindex/pipeline/run.py:31`의 `_TsWriter`는 `write`, `flush`만 정의하고 나머지는 원래 stdout에 넘깁니다.

```python
def __getattr__(self, name):
    return getattr(self._raw, name)

def _install_ts_stdout():
    if not isinstance(sys.stdout, _TsWriter):
        sys.stdout = _TsWriter(sys.stdout)
```

upstream이 `client.chat.completions.create(...)`처럼 긴 경로로 부르는 경우에는, `chat`과 `completions`를
`self`를 돌려주는 property로 만들어 같은 경로를 흉내 냅니다(`adapters/browsecomp/agent/or_client_ours.py:19`의
`_Routed`).

## 주의할 점

proxy는 원래 객체와 타입이 다르므로 `isinstance` 검사까지 통과해야 하는 상황에는 맞지 않습니다. 그럴 때는
상속([B4](b4-mixin.md))을 씁니다.
