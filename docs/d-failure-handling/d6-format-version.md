---
sidebar_position: 6
sidebar_label: "D6. 저장 형식 version"
description: "저장 형식에 version을 넣고, 읽을 때 version, shape, 수치를 검사하는 방법입니다."
---

# 저장 형식 version

저장 형식에 version을 넣고, 읽을 때 version, shape, 수치를 검사하는 방법입니다.

## 사용 방법

- 저장하는 쪽은 version 필드를 함께 씁니다.
- 읽는 쪽은 파일이 없으면 고치는 방법을 알리고, version이 다르면 거부합니다.
- numpy 파일은 `allow_pickle=False`로 열고, 배열의 차원, dtype, 유한성, 값 범위를 검사합니다.

## 왜 필요한가

형식이 바뀐 이전 파일을 읽었을 때, 엉뚱한 값으로 계속 돌지 않고 읽는 순간 실패합니다. `allow_pickle=False`는
신뢰할 수 없는 파일이 임의 코드를 실행하는 경로를 막습니다.

## Self-Index에서의 사용

`MemoryKeyState.save`/`load`(`adapters/longmem/adapter/key_state.py:59`, `:75`).
