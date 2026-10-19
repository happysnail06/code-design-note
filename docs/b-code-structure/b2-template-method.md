---
sidebar_position: 2
sidebar_label: "B2. Template method와 hook"
description: "하위 클래스가 채우는 `build()`와 바깥에서 부르는 `create()`를 나눠서, 확장 코드의 실수를 경계에서 잡는 방법입니다."
---

# Template method와 hook

하위 클래스가 채우는 `build()`와 바깥에서 부르는 `create()`를 나눠서, 확장 코드의 실수를 경계에서 잡는
방법입니다.

## 개념

- **template method**는 기본 클래스가 처리 순서를 정하고, 하위 클래스는 그중 일부 단계만 채우는 설계입니다.
- **hook**은 하위 클래스가 원할 때만 override하는, 기본 동작이 비어 있는 메서드입니다.

## 사용 방법

- 확장하는 사람이 구현할 메서드(`build`)와 바깥에서 부르는 메서드(`create`)를 나눕니다.
- `create`는 `build`를 부른 뒤 돌려받은 값의 타입과 조건을 검사합니다.
- 하위 클래스가 필요할 때만 override하는 hook은 빈 일반 메서드로 둡니다.
- 정리를 맡는 hook은 공개 메서드가 `try/finally`로 불러서, 본 작업이 실패해도 항상 실행되게 합니다.

## 왜 필요한가

확장 코드가 잘못된 타입을 반환하면 `create()`에서 즉시 오류를 냅니다. 잘못된 값이 다른 단계로 전달되기 전에
어떤 구현이 반환 형식을 위반했는지 확인할 수 있습니다.

## 예시

```python
# 예시: build는 하위 클래스가, 검사는 기본 클래스의 create가 맡습니다
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    name: str


class Factory(ABC):
    def create(self, name: str) -> Task:
        # 하위 클래스가 만든 결과가 약속한 타입인지 경계에서 확인합니다
        result = self.build(name)
        if not isinstance(result, Task):
            raise TypeError(f"{type(self).__name__}.build() must return Task")
        return result

    @abstractmethod
    def build(self, name: str) -> Task: ...


class GoodFactory(Factory):
    def build(self, name: str) -> Task:
        return Task(name)


class BadFactory(Factory):
    def build(self, name: str) -> Task:
        return name  # 실수로 문자열을 돌려줍니다


print(GoodFactory().create("encode"))  # Task(name='encode')
try:
    BadFactory().create("encode")
except TypeError as error:
    print(error)  # BadFactory.build() must return Task
```

## Self-Index에서의 사용

`src/selfindex/runtime/factories.py:52`. 같은 형태가 `runtime/catalog/retrievers.py:24`,
`adapters/browsecomp/adapters/search_factory.py:53`에도 있습니다.

```python
@abstractmethod
def build(self, task: str, argv: list) -> Task: ...

def create(self, task, argv):
    self.validate_task(task)
    result = self.build(task, list(argv))
    if not isinstance(result, Task):
        raise TypeError("factory build() must return Task")
    return result
```

선택 hook과 정리 hook은 `adapters/browsecomp/agent/backbones.py:73`, `:98`에 있습니다.

```python
def pre_agent(self, log_dir):  # noqa: B027
    ...

def run_agent(self, queries, out_dir, threads, log_path):
    try:
        self.pre_agent(os.path.dirname(log_path) or ".")
        return self._run_process(queries, out_dir, threads, log_path)
    finally:
        self.post_agent()
```

`B027`은 "ABC 안의 빈 메서드가 abstract가 아니다"라는 flake8-bugbear 경고입니다. 이 레포는 의도한 hook이라는
표시로 그 줄에서만 경고를 끕니다.
