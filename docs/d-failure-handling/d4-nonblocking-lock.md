---
sidebar_position: 4
sidebar_label: "D4. 기다리지 않는 파일 lock"
description: "여러 프로세스가 같은 산출물을 쓰려 하면 기다리지 않고 바로 실패시키는 방법입니다."
---

# 기다리지 않는 파일 lock

여러 프로세스가 같은 산출물을 쓰려 하면 기다리지 않고 바로 실패시키는 방법입니다.

## 개념

`fcntl.flock(f, LOCK_EX | LOCK_NB)`는 파일에 배타 lock을 걸되, 이미 다른 프로세스가 잡고 있으면 기다리지 않고
바로 `BlockingIOError`를 냅니다.

## 사용 방법

lock을 잡지 못하면 "another build is publishing ..."처럼 무슨 일이 일어났는지 말하는 오류로 바꿔 올립니다.

## 왜 필요한가

두 프로세스가 같은 산출물을 동시에 쓰면 결과가 섞입니다. 기다리게 하면 사용자는 왜 멈춰 있는지 모릅니다.

## Self-Index에서의 사용

`build_bm25_index.py:50`, `runtime/workflows/execution.py:48`.
