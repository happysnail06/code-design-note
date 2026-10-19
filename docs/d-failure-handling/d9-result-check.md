---
sidebar_position: 9
sidebar_label: "D9. 결과 검사"
description: "다음 단계로 넘기기 전에 결과의 개수와 수치를 검사하는 방법입니다."
---

# 결과 검사

다음 단계로 넘기기 전에 결과의 개수와 수치를 검사하는 방법입니다.

## 사용 방법

점수 block이 query 수보다 많아도, 적어도, 비어 있어도, NaN이 섞여도 실패시킵니다.

## 왜 필요한가

개수가 어긋난 결과를 평균 내면 숫자는 나오지만 틀린 숫자입니다. 이런 오류는 나중에 발견하기 가장 어렵습니다.

## Self-Index에서의 사용

`PipelineEvaluation.measure`(`evaluation/evaluator.py:24`).
