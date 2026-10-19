---
sidebar_position: 0
sidebar_label: "이 절의 주제"
---

# D. 실패에 대비하는 방법

실행 중단, 동시 실행, 외부 호출 실패에 대비해 산출물과 상태를 보호하는 방법을 다룹니다. 관찰 원본은
`self-index-coding-conventions.md`의 9~13절에 있습니다.

## 주제

- **[D1. Atomic replace](d1-atomic-replace.md)**: 임시 파일에 다 쓴 뒤 한 번에 교체해서, 반쯤 쓴 파일이 남지 않게 하는 방법입니다.
- **[D2. 디렉터리 교체와 backup](d2-directory-swap.md)**: 새 디렉터리를 따로 완성하고, 이전 것을 backup으로 옮긴 뒤 교체하는 방법입니다.
- **[D3. 되돌릴 수 있는 순서](d3-reversible-order.md)**: 실패할 수 있는 단계를 먼저, 되돌리기 어려운 단계를 나중에 하는 방법입니다.
- **[D4. 기다리지 않는 파일 lock](d4-nonblocking-lock.md)**: 여러 프로세스가 같은 산출물을 쓰려 하면 기다리지 않고 바로 실패시키는 방법입니다.
- **[D5. 재개 검증](d5-resume-check.md)**: 중단된 작업을 재개하기 전에 해시로 실행 조건과 산출물이 같은지 확인하는 방법입니다.
- **[D6. 저장 형식 version](d6-format-version.md)**: 저장 형식에 version을 넣고, 읽을 때 version, shape, 수치를 검사하는 방법입니다.
- **[D7. 외부 코드 전제 검사](d7-upstream-check.md)**: adapter가 기대는 외부 코드의 전제를 실행 전에 검사하는 방법입니다.
- **[D8. 재시도할 오류 구분](d8-retry-classes.md)**: 재시도해도 소용없는 오류와 일시적인 오류를 나누고, 재시도 정책은 한 곳에서 정하는 방법입니다.
- **[D9. 결과 검사](d9-result-check.md)**: 다음 단계로 넘기기 전에 결과의 개수와 수치를 검사하는 방법입니다.
