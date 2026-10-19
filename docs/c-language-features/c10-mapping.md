---
sidebar_position: 10
sidebar_label: "C10. Mapping"
description: "읽기 전용 표를 `collections.abc.Mapping`의 세 메서드만으로 만드는 방법입니다."
---

# Mapping

읽기 전용 표를 `collections.abc.Mapping`의 세 메서드만으로 만드는 방법입니다.

## 개념

Mapping은 dict처럼 읽을 수 있는 객체의 추상 클래스입니다. `__getitem__`, `__iter__`, `__len__` 세 개만 구현하면
나머지 읽기 기능을 물려받습니다.

## 사용 방법

- 세 메서드만 구현하면 `in`, `.items()`, `.get()`, `sorted()`가 모두 동작합니다.
- `__setitem__`이 없어서 바깥에서 항목을 덮어쓸 수 없습니다.
- 항목은 검증을 수행하는 `register()`로만 추가합니다.

예시는 B3에 있습니다.

## Self-Index에서의 사용

`src/selfindex/runtime/registry.py:9`의 `class Registry(Mapping[str, T], Generic[T])`. 레포에서 타입 표기가 가장
충실한 파일이기도 합니다.
