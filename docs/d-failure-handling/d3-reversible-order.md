---
sidebar_position: 3
sidebar_label: "D3. 되돌릴 수 있는 순서"
description: "실패할 수 있는 단계를 먼저, 되돌리기 어려운 단계를 나중에 하는 방법입니다."
---

# 되돌릴 수 있는 순서

실패할 수 있는 단계를 먼저, 되돌리기 어려운 단계를 나중에 하는 방법입니다.

## 사용 방법

항목을 교체할 때는 새 항목 추가를 먼저 하고, 성공한 뒤에야 이전 항목을 지웁니다.

## 왜 필요한가

추가가 실패해도 이전 항목이 그대로 있으므로, 되돌릴 때는 추가하던 것만 지우면 됩니다. 순서를 반대로 하면 지운 뒤
추가가 실패했을 때 이전 항목을 복구할 방법이 없습니다.

## 예시

```python
# 예시: 추가를 먼저, 삭제를 나중에 합니다
def replace_keys(index: list[str], old: list[str], new: list[str]) -> None:
    start = len(index)
    try:
        # 실패할 수 있는 단계: 새 key를 검사하며 추가합니다
        for key in new:
            if not key:
                raise ValueError("key must not be empty")
            index.append(key)
    except BaseException:
        # 추가하던 것만 지우면 원래 상태로 돌아갑니다
        del index[start:]
        raise

    # 추가가 모두 성공한 뒤에야 이전 key를 지웁니다
    for key in old:
        index.remove(key)


keys = ["apple"]
try:
    replace_keys(keys, ["apple"], ["pear", ""])
except ValueError:
    pass
print(keys)  # ['apple'] — 실패했지만 이전 상태가 그대로입니다
replace_keys(keys, ["apple"], ["pear"])
print(keys)  # ['pear']
```

## Self-Index에서의 사용

`_replace_encoded`(`index/dense.py:302`). 추가가 실패하면 shard별 count와 text 목록만 원래 길이로 돌립니다.
