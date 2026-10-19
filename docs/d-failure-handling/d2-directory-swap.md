---
sidebar_position: 2
sidebar_label: "D2. 디렉터리 교체와 backup"
description: "새 디렉터리를 따로 완성하고, 이전 것을 backup으로 옮긴 뒤 교체하는 방법입니다."
---

# 디렉터리 교체와 backup

새 디렉터리를 따로 완성하고, 이전 것을 backup으로 옮긴 뒤 교체하는 방법입니다.

## 사용 방법

1. 새 디렉터리를 임시 위치(staging)에서 끝까지 만듭니다.
2. 비어 있는 결과는 먼저 거부합니다.
3. 기존 디렉터리를 backup 이름으로 옮기고, 새 디렉터리를 제자리에 놓습니다.
4. 교체가 실패하면 backup을 원래 이름으로 되돌립니다.

## Self-Index에서의 사용

`_publish_index`(`build_bm25_index.py:62`). 같은 장치면 rename, 다른 장치면 copytree로 옮깁니다.
