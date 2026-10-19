---
sidebar_position: 5
sidebar_label: "C5. Staticmethod"
description: "`self`도 `cls`도 받지 않는 staticmethod를 private helper에만 쓰는 방법입니다."
---

# Staticmethod

`self`도 `cls`도 받지 않는 staticmethod를 private helper에만 쓰는 방법입니다.

## 개념

staticmethod(`@staticmethod`)는 `self`도 `cls`도 받지 않는 메서드입니다. 클래스 안에 둔 일반 함수와 같습니다.

## 사용 방법

그 클래스 안에서만 쓰는 helper에만 쓰고, 이름은 `_`로 시작합니다. 다른 곳에서도 쓸 순수 함수는 클래스 밖의 모듈
함수로 둡니다.

## 왜 필요한가

`self`를 쓰지 않는다는 사실이 시그니처에 드러나고, 그 클래스 안에서만 쓰는 helper라는 위치도 유지됩니다.

## Self-Index에서의 사용

레포의 `@staticmethod` 6개는 모두 `_`로 시작합니다: `_checked_block`, `_units`, `_query_file`,
`_write_query_records`, `_best_per_document`, `_search_adapter`.
