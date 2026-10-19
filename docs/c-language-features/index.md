---
sidebar_position: 0
sidebar_label: "이 절의 주제"
---

# C. decorator와 언어 기능

decorator와 Python 언어 기능의 용도와 선택 기준을 다룹니다. 레포 전체의 decorator 사용 횟수는
다음과 같습니다(AST 집계).

| decorator | 횟수 | 이 레포에서의 용도 |
|---|---|---|
| `@abstractmethod` | 36 | interface의 필수 메서드 |
| `@property` | 28 | 파생 값, 지연 로드, 추상 속성, 상태를 확인한 뒤 돌려주는 값 |
| `@dataclass(frozen=True)` | 20 | spec, plan, settings, 판정 결과 같은 바뀌지 않는 값 |
| `@dataclass` | 13 | 실행 중 바뀌는 상태와 집계 |
| `@classmethod` | 10 | 이름 있는 생성자, 객체 없이 하는 검사, 등록 decorator |
| `@staticmethod` | 6 | 모두 `_`로 시작하는 private helper |
| `@contextmanager` | 4 | 되돌리기가 보장되어야 하는 일시적 변경과 lock |
| `@register_memory` 외 등록 decorator | 4 | 클래스를 registry에 등록 |
| `@cache` | 1 | 외부 서비스 조회 결과 캐시 |

## 주제

- **[C1. Dataclass](c1-dataclass.md)**: 바뀌지 않는 값은 frozen dataclass로, 바뀌는 상태는 일반 dataclass로 만드는 방법입니다.
- **[C2. NamedTuple](c2-namedtuple.md)**: 풀어서 받는 작은 반환값과 JSON으로 내보낼 작은 레코드를 만드는 방법입니다.
- **[C3. Property](c3-property.md)**: 메서드를 속성처럼 읽게 하는 property를 쓰는 네 가지 경우입니다.
- **[C4. Classmethod](c4-classmethod.md)**: 클래스를 첫 인자로 받는 classmethod를 쓰는 세 가지 경우입니다.
- **[C5. Staticmethod](c5-staticmethod.md)**: `self`도 `cls`도 받지 않는 staticmethod를 private helper에만 쓰는 방법입니다.
- **[C6. Abstract method](c6-abstract-method.md)**: 모든 구현이 가져야 하는 기능은 abstract method로, 일부 구현만 지원하는 기능은 이유를 밝히는 오류로 두는 방법입니다.
- **[C7. Context manager](c7-context-manager.md)**: 한 함수 안에서 상태를 바꾸고 복원할 때는 `@contextmanager`, 객체의 자원 사용과 정리를 관리할 때는 `__enter__`/`__exit__`를 쓰는 방법입니다.
- **[C8. Cache](c8-cache.md)**: 성공한 외부 조회만 기억하게 해서 같은 조회를 한 번만 하는 방법입니다.
- **[C9. `__init_subclass__`](c9-init-subclass.md)**: 하위 클래스를 정의하는 순간 자동으로 등록하는 방법입니다.
- **[C10. Mapping](c10-mapping.md)**: 읽기 전용 표를 `collections.abc.Mapping`의 세 메서드만으로 만드는 방법입니다.
- **[C11. BaseException](c11-base-exception.md)**: 외부 코드의 `except Exception`에 잡히면 안 되는 신호를 만드는 방법입니다.
- **[C12. 작은 언어 기능](c12-small-features.md)**: 자주 쓰이는 작은 Python 기법을 모았습니다.
