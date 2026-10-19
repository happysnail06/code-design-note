---
sidebar_position: 5
sidebar_label: "D5. 재개 검증"
description: "중단된 작업을 재개하기 전에 해시로 실행 조건과 산출물이 같은지 확인하는 방법입니다."
---

# 재개 검증

중단된 작업을 재개하기 전에 해시로 실행 조건과 산출물이 같은지 확인하는 방법입니다.

## 사용 방법

- 단계가 끝날 때마다 산출물의 sha256을 기록(receipt)하고, 이어서 실행할 때 다시 해시해서 비교합니다.
- 설정 환경 변수, 소스 코드, 입력 파일의 해시(실행 identity)도 기록해 두고, 하나라도 다르면 이어서 실행하지
  않습니다.
- 단계 상태(`running`, `failed`, `complete`)와 실패한 예외 타입 이름은 `workflow_status.json`에 원자적으로
  씁니다.

## 왜 필요한가

설정이나 코드가 바뀐 뒤 이전 실행의 중간 결과를 이어 붙이면, 서로 다른 조건의 결과가 섞인 산출물이 나옵니다.
이런 결과는 겉보기로는 구분할 수 없습니다.

## Self-Index에서의 사용

`WorkflowCheckpoint`(`runtime/workflows/checkpoints.py:43`)가 실행 identity와 산출물 해시를 확인하고,
`StageRunner`(`runtime/workflows/execution.py:54`)가 완료한 단계를 건너뛰고 나머지를 실행합니다.

결과가 어떤 조건에서 만들어졌는지 추적하는 **provenance**도 기록합니다.
`ProvenanceWriter.write()`(`storage/provenance.py:90`)는 소스 복사본을 `src/`에 저장하고,
소스 해시, git HEAD와 변경 여부, Python·패키지 버전을 `src/manifest.json`에 기록합니다.
데이터 fingerprint와 설정 정보는 `run_config.json`에 저장합니다
(`pipeline/run.py:219`). 재개 시 검증과 함께, 나중에 서로 다른 실행 결과의 조건을 비교하는 데 쓰입니다.
