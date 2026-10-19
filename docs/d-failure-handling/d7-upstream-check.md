---
sidebar_position: 7
sidebar_label: "D7. 외부 코드 전제 검사"
description: "adapter가 기대는 외부 코드의 전제를 실행 전에 검사하는 방법입니다."
---

# 외부 코드 전제 검사

adapter가 기대는 외부 코드의 전제를 실행 전에 검사하는 방법입니다.

## 사용 방법

judge evaluator를 불러올 때 upstream 스크립트를 AST로 읽어, 예상한 import가 정확히 하나 있는지 확인합니다.
다르면 "upstream evaluator inference contract changed; review the adapter"로 멈춥니다.

## 왜 필요한가

upstream을 새 버전으로 바꿨을 때 adapter가 조용히 잘못 도는 대신, 시작할 때 무엇을 다시 봐야 하는지 알려 줍니다.

## Self-Index에서의 사용

`adapters/browsecomp/adapters/judging.py:72`.
