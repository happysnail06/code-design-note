---
sidebar_position: 3
sidebar_label: "한눈에 보기"
---

# 한눈에 보기

## A. 프로젝트 구성과 실행 흐름

- **[A1. Adapter와 upstream](a-repo-structure/a1-adapter-upstream.md)**: 외부 서비스, 외부 라이브러리, 다른 저장소의 코드와 닿는 부분을 adapter 한 곳에
  모으고, 가져온 외부 코드는 고치지 않습니다.
- **[A2. Lazy import](a-repo-structure/a2-lazy-import.md)**: 일부 기능에서만 필요한 모듈은 그 기능을 실행하는 함수 안에서 import해서, 그 모듈이
  없는 환경에서도 나머지 기능이 돌게 합니다.
- **[A3. 단일 진입점과 명령 표](a-repo-structure/a3-entry-point.md)**: 모든 실행, 하위 프로세스까지 하나의 진입점과 명령 표를 거치게 해서 import
  경로와 환경을 하나로 맞춥니다.
- **[A4. 실행 전 전체 검증](a-repo-structure/a4-validate-first.md)**: 할 일 전체를 plan으로 만들고 모두 검증한 뒤에 첫 단계를 실행합니다.
- **[A5. 소스 파일 기준 경로](a-repo-structure/a5-source-paths.md)**: 경로를 작업 디렉터리가 아니라 소스 파일 위치에서 계산해서, 어디서 실행해도
  같은 파일을 가리키게 합니다.
- **[A6. 저장소 문서의 역할 분담](a-repo-structure/a6-repo-docs.md)**: 문서마다 맡는 내용을 나누고, 코드의 설정 표와 문서의 표를 맞춰 둡니다.

## B. 인터페이스와 객체 설계

- **[B1. ABC와 Protocol](b-code-structure/b1-abc-protocol.md)**: interface와 구현을 다른 파일에 두고, 상속은 한두 단계에서 끝냅니다.
- **[B2. Template method와 hook](b-code-structure/b2-template-method.md)**: 하위 클래스가 채우는 `build()`와 바깥에서 부르는 `create()`를 나눠서,
  확장 코드의 실수를 경계에서 잡습니다.
- **[B3. Registry](b-code-structure/b3-registry.md)**: 구현을 이름으로 등록하고 이름으로 꺼내 씁니다. 등록할 때 이름 중복과 추상 클래스를
  거부합니다.
- **[B4. Mixin](b-code-structure/b4-mixin.md)**: 외부 클래스를 고치지 않고, 함께 상속하는 작은 클래스로 기능을 덧붙입니다.
- **[B5. Proxy](b-code-structure/b5-proxy.md)**: 객체를 감싸서 일부 메서드만 바꾸고 나머지는 원래 객체에 넘깁니다.
- **[B6. Callable](b-code-structure/b6-callable.md)**: 실행할 동작을 함수, lambda, 호출 가능한 객체로 전달받습니다.
- **[B7. Context와 상태 객체](b-code-structure/b7-context-state.md)**: 단계 사이에 넘기는 값 묶음에서 입력과, 실행 중 바뀌는 상태를 나눠 담습니다.

## C. decorator와 언어 기능

- **[C1. Dataclass](c-language-features/c1-dataclass.md)**: 바뀌지 않는 값은 frozen dataclass, 바뀌는 상태는 일반 dataclass로 만듭니다.
- **[C2. NamedTuple](c-language-features/c2-namedtuple.md)**: 풀어서 받는 작은 반환값과 JSON으로 내보낼 작은 레코드에 씁니다.
- **[C3. Property](c-language-features/c3-property.md)**: 파생 값, 지연 로드, 추상 속성, 상태를 확인해야 하는 값의 네 경우에 씁니다.
- **[C4. Classmethod](c-language-features/c4-classmethod.md)**: 이름 있는 생성자, 객체 없이 하는 검사, 등록 decorator에 씁니다.
- **[C5. Staticmethod](c-language-features/c5-staticmethod.md)**: 그 클래스 안에서만 쓰는 private helper에만 씁니다.
- **[C6. Abstract method](c-language-features/c6-abstract-method.md)**: 필수 기능은 abstract method로, 일부 구현만 지원하는 기능은 이유를 밝히는 오류로
  둡니다.
- **[C7. Context manager](c-language-features/c7-context-manager.md)**: 한 함수 안에서 상태를 바꾸고 복원할 때는 `@contextmanager`, 객체의 자원 사용과
  정리를 관리할 때는 `__enter__`/`__exit__`를 씁니다.
- **[C8. Cache](c-language-features/c8-cache.md)**: 성공한 외부 조회만 기억하게 해서 같은 조회를 한 번만 합니다.
- **[C9](c-language-features/c9-init-subclass.md) `__init_subclass__`**: 하위 클래스를 정의하는 순간 자동으로 등록합니다.
- **[C10. Mapping](c-language-features/c10-mapping.md)**: 읽기 전용 표를 세 메서드만으로 만듭니다.
- **[C11. BaseException](c-language-features/c11-base-exception.md)**: 외부 코드의 `except Exception`에 잡히면 안 되는 신호를 만듭니다.
- **[C12. 작은 언어 기능](c-language-features/c12-small-features.md)**: walrus, keyword-only argument, `zip(strict=True)`, sentinel 같은 기법을 모았습니다.

## D. 실패에 대비하는 방법

- **[D1. Atomic replace](d-failure-handling/d1-atomic-replace.md)**: 임시 파일에 다 쓴 뒤 한 번에 교체해서 반쯤 쓴 파일이 남지 않게 합니다.
- **[D2. 디렉터리 교체와 backup](d-failure-handling/d2-directory-swap.md)**: 새 디렉터리를 따로 완성하고, 이전 것을 backup으로 옮긴 뒤 교체합니다.
- **[D3. 되돌릴 수 있는 순서](d-failure-handling/d3-reversible-order.md)**: 실패할 수 있는 단계를 먼저, 되돌리기 어려운 단계를 나중에 합니다.
- **[D4. 기다리지 않는 파일 lock](d-failure-handling/d4-nonblocking-lock.md)**: 여러 프로세스가 같은 산출물을 쓰려 하면 기다리지 않고 바로 실패시킵니다.
- **[D5. 재개 검증](d-failure-handling/d5-resume-check.md)**: 중단된 작업을 재개하기 전에 해시로 실행 조건과 산출물이 같은지 확인합니다.
- **[D6. 저장 형식 version](d-failure-handling/d6-format-version.md)**: 저장 형식에 version을 넣고, 읽을 때 version, shape, 수치를 검사합니다.
- **[D7. 외부 코드 전제 검사](d-failure-handling/d7-upstream-check.md)**: adapter가 기대는 외부 코드의 전제를 실행 전에 검사합니다.
- **[D8. 재시도할 오류 구분](d-failure-handling/d8-retry-classes.md)**: 재시도해도 소용없는 오류와 일시적인 오류를 나누고, 재시도 정책은 한 곳에서
  정합니다.
- **[D9. 결과 검사](d-failure-handling/d9-result-check.md)**: 다음 단계로 넘기기 전에 결과의 개수와 수치를 검사합니다.

## E. 설계할 때 주의할 점

실패와 정상 결과의 구분, 입력 검증, 상태 관리, 공통 설정, 공개 interface를 설계할 때의 주의점과 판단 기준을 정리했습니다.
