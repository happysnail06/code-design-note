---
sidebar_position: 6
sidebar_label: "A6. 저장소 문서의 역할 분담"
description: "문서마다 맡는 내용을 나누고, 코드의 설정 표와 문서의 표를 맞춰 두는 방법입니다."
---

# 저장소 문서의 역할 분담

문서마다 맡는 내용을 나누고, 코드의 설정 표와 문서의 표를 맞춰 두는 방법입니다.

## 사용 방법

| 문서 | 맡는 내용 |
|---|---|
| `README.md` | 설치, 환경 변수, 파라미터, 확장 방법 |
| `docs/REPRODUCING.md` | 보고된 수치를 재현하는 명령 |
| `docs/ARTIFACTS.md` | 산출물 파일의 형식과 필드 |
| `externals/README.md` | upstream 출처와 license |

README의 파라미터 표는 코드의 `PARAMETERS` dict와 같은 내용입니다.

## 왜 필요한가

사용자가 알아야 하는 사실이 한 문서에 몰리지 않습니다. 코드의 설정 dict를 바꿀 때 함께 고쳐야 할 문서 위치도
정해져 있습니다.
