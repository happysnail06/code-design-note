---
sidebar_position: 4
sidebar_label: "B4. Mixin"
description: "외부 클래스를 고치지 않고, 함께 상속하는 작은 클래스로 기능을 덧붙이는 방법입니다."
---

# Mixin

외부 클래스를 고치지 않고, 함께 상속하는 작은 클래스로 기능을 덧붙이는 방법입니다.

## 개념

- **mixin**은 혼자서는 쓰지 않고 다른 클래스와 함께 상속해서 기능을 덧붙이는 작은 클래스입니다.
- `class Ours(Mixin, Upstream)`이라고 쓰면 메서드를 Ours, Mixin, Upstream 순서로 찾습니다. 이 순서를
  **MRO**라고 합니다. 그래서 Mixin의 메서드가 먼저 불리고, 그 안의 `super()`는 Upstream의 같은 메서드를
  부릅니다.

## 사용 방법

- upstream 클래스를 고치지 않고 `class Ours(Mixin, Upstream)` 형태로 합칩니다.
- mixin 메서드는 `super()`를 부르고, 그 앞뒤에 동작을 덧붙입니다.
- upstream이 모르는 설정 키는 `super().__init__`에 넘기기 전에 빼냅니다.
- mixin이 추가하는 속성에는 `_si_keys`처럼 mixin 고유의 접두어를 붙입니다.

## 왜 필요한가

upstream 코드를 한 줄도 고치지 않으므로 upstream을 새 버전으로 바꾸기 쉽습니다. 접두어 덕분에 upstream이 나중에
같은 이름의 속성을 추가해도 서로 덮어쓰지 않습니다.

## 예시

```python
# 예시: upstream의 Memory를 고치지 않고 추가 건수를 세는 기능을 덧붙입니다
class Memory:
    """upstream 클래스라고 가정합니다. 이 코드는 고치지 않습니다."""

    def __init__(self, params: dict) -> None:
        self.size = params["size"]
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)


class CountingMixin:
    def __init__(self, params: dict) -> None:
        # upstream이 모르는 설정 키는 넘기기 전에 빼냅니다
        params = dict(params)
        self._counting_label = params.pop("label", "memory")
        super().__init__(params)
        self._counting_added = 0

    def add(self, item: str) -> None:
        # upstream 동작을 먼저 하고, 그 뒤에 건수를 셉니다
        super().add(item)
        self._counting_added += 1


class CountingMemory(CountingMixin, Memory):
    pass


memory = CountingMemory({"size": 3, "label": "notes"})
memory.add("first")
print(memory.items, memory._counting_added)  # ['first'] 1
print([cls.__name__ for cls in CountingMemory.__mro__])
# ['CountingMemory', 'CountingMixin', 'Memory', 'object']
```

## Self-Index에서의 사용

`adapters/longmem/adapter/memory_ours.py:17`, `:104`

```python
class SelfIndexMixin:

    def __init__(self, memory_params):
        params = dict(memory_params)
        keys_path = params.pop("selfindex_keys_path", None)
        super().__init__(params)
        self._selfindex_init(keys_path)
    ...

@register_memory
class RagSelfIndex(SelfIndexMixin, RagMemory):
    memory_type = "rag_selfindex"
```

## 주의할 점

upstream이 내부 메서드 이름을 바꾸면 mixin의 override가 더 이상 불리지 않는데, 오류도 나지 않습니다. 이 레포는
다른 adapter에서 upstream의 전제를 실행 전에 검사하는 방식으로 이 위험을 다룹니다([D7](../d-failure-handling/d7-upstream-check.md)).
