---
sidebar_position: 2
sidebar_label: "먼저 알아 둘 개념"
---

# 먼저 알아 둘 개념

용어는 영어로 적고, 설명은 한국어로 적었습니다. Python 코드에서 쓰는 형태는 "Python 표기" 열에 따로
두었습니다.

## 설계 개념

언어와 상관없이 쓰는 설계 용어입니다.

| 용어 | 설명 | 관련 주제 |
|---|---|---|
| interface | 구현이 지켜야 하는 약속입니다. "어떤 이름의 메서드가 어떤 인자를 받아 무엇을 돌려준다"를 정합니다. 이 레포는 interface를 담은 파일을 `contracts.py`라고 부릅니다. | [B1](b-code-structure/b1-abc-protocol.md) |
| adapter | 외부 서비스, 외부 라이브러리, 다른 저장소의 코드를 부르고, 그 입출력을 우리 코드의 형식으로 바꿔 주는 코드입니다. | [A1](a-repo-structure/a1-adapter-upstream.md) |
| upstream | 우리가 가져다 쓰는 다른 저장소의 원본 코드입니다. 이 레포에서는 benchmark 저장소들이 upstream입니다. | [A1](a-repo-structure/a1-adapter-upstream.md), [B4](b-code-structure/b4-mixin.md) |
| lazy import | 파일 첫머리가 아니라, 그 모듈이 필요한 함수 안에서 하는 import입니다. 함수를 부를 때에야 import됩니다. | [A2](a-repo-structure/a2-lazy-import.md) |
| template method | 기본 클래스가 처리 순서를 정하고, 하위 클래스는 그중 일부 단계만 채우는 설계 방식입니다. | [B2](b-code-structure/b2-template-method.md) |
| hook | 하위 클래스가 원할 때만 override하는, 기본 동작이 비어 있는 메서드입니다. | [B2](b-code-structure/b2-template-method.md) |
| registry | 이름을 키로 구현을 등록해 두고, 실행할 때 이름으로 꺼내 쓰는 표입니다. | [B3](b-code-structure/b3-registry.md) |
| mixin | 혼자서는 쓰지 않고, 다른 클래스와 함께 상속해서 기능을 덧붙이는 작은 클래스입니다. | [B4](b-code-structure/b4-mixin.md) |
| MRO | Method Resolution Order의 약자로, 여러 클래스를 상속했을 때 메서드를 찾는 순서입니다. `class C(A, B)`이면 C, A, B 순서로 찾고, `super()`는 이 순서에서 다음 클래스를 가리킵니다. | [B4](b-code-structure/b4-mixin.md) |
| proxy | 원래 객체를 속성으로 보관하고, 일부 메서드만 바꾸고 나머지는 원래 객체에 넘기는 객체입니다. wrapper라고도 부릅니다. | [B5](b-code-structure/b5-proxy.md) |
| dependency injection | 필요한 객체나 함수를 내부에서 생성하지 않고 인자로 전달받는 방식입니다. | [B1](b-code-structure/b1-abc-protocol.md) |
| strategy | 같은 역할의 구현을 교체할 수 있도록 공통 interface로 분리한 동작입니다. | [B1](b-code-structure/b1-abc-protocol.md) |
| snapshot과 read lease | snapshot은 조회할 index 상태를 일정하게 유지하고, read lease는 조회가 끝날 때까지 변경을 제한합니다. | [C7](c-language-features/c7-context-manager.md) |
| checkpoint | 완료한 단계와 산출물을 기록해 중단된 실행을 재개할 때 확인하는 정보입니다. | [D5](d-failure-handling/d5-resume-check.md) |
| provenance | 결과를 만든 코드, 설정, 데이터, 실행 환경의 기록입니다. | [D5](d-failure-handling/d5-resume-check.md) |
| sentinel | "값이 없음"을 표시하려고 만든 특별한 객체입니다. `None`도 정상 값으로 쓰일 때 필요합니다. | [C7](c-language-features/c7-context-manager.md), [C12](c-language-features/c12-small-features.md) |
| atomic replace | 새 파일을 다 쓴 뒤 한 번에 교체하는 것입니다. 다른 프로세스는 이전 파일 아니면 완성된 새 파일만 보게 됩니다. | [D1](d-failure-handling/d1-atomic-replace.md) |

## 클래스와 타입

Python에서 클래스와 타입을 정의할 때 쓰는 기능입니다.

| 용어 | Python 표기 | 설명 | 관련 주제 |
|---|---|---|---|
| ABC | `abc.ABC` | Abstract Base Class의 약자로, interface를 클래스로 표현한 것입니다. 미구현 abstract method가 남아 있으면 객체를 만들 수 없습니다. | [B1](b-code-structure/b1-abc-protocol.md), [C6](c-language-features/c6-abstract-method.md) |
| abstract method | `@abstractmethod` | ABC 안에서 "하위 클래스가 반드시 구현해야 하는 메서드"를 표시합니다. 하나라도 구현하지 않은 하위 클래스로 객체를 만들면 `TypeError`가 납니다. | [B1](b-code-structure/b1-abc-protocol.md), [C6](c-language-features/c6-abstract-method.md) |
| Protocol | `typing.Protocol` | 상속하지 않아도, 정해진 메서드만 가지고 있으면 같은 타입으로 인정하는 interface입니다. 타입 검사기가 확인하고, 실행 중에는 아무것도 강제하지 않습니다. | [B1](b-code-structure/b1-abc-protocol.md), [B6](b-code-structure/b6-callable.md) |
| dataclass | `@dataclass` | 필드만 적으면 `__init__`, `__repr__`, `__eq__`를 자동으로 만들어 주는 decorator입니다. | [C1](c-language-features/c1-dataclass.md) |
| frozen dataclass | `@dataclass(frozen=True)` | 만든 뒤에는 필드에 다시 대입할 수 없는 dataclass입니다. 대입하면 `FrozenInstanceError`가 납니다. | [C1](c-language-features/c1-dataclass.md) |
| NamedTuple | `typing.NamedTuple` | 필드 이름이 붙은 tuple입니다. `a, b = result`처럼 풀어서 받을 수 있고 `result.a`처럼 이름으로도 읽을 수 있습니다. | [C2](c-language-features/c2-namedtuple.md) |
| Mapping | `collections.abc.Mapping` | dict처럼 읽을 수 있는 객체의 추상 클래스입니다. 세 메서드만 구현하면 `in`, `.get()`, `.items()`가 따라옵니다. | [C10](c-language-features/c10-mapping.md) |
| MappingProxyType | `types.MappingProxyType` | dict를 읽기 전용으로 보여 주는 표준 라이브러리 타입입니다. | [C1](c-language-features/c1-dataclass.md) |
| Callable | `collections.abc.Callable` | "괄호를 붙여 부를 수 있는 것"을 뜻하는 타입입니다. 함수, lambda, `__call__`을 가진 객체가 모두 해당합니다. | [B6](b-code-structure/b6-callable.md) |

## decorator

함수나 클래스 정의 위에 `@`로 붙이는 기능입니다.

| 용어 | Python 표기 | 설명 | 관련 주제 |
|---|---|---|---|
| property | `@property` | 메서드를 속성처럼 읽게 합니다. `obj.size()` 대신 `obj.size`로 씁니다. | [C3](c-language-features/c3-property.md) |
| classmethod | `@classmethod` | 객체가 아니라 클래스를 첫 인자(`cls`)로 받는 메서드를 만듭니다. 객체 없이 `ClassName.method()`로 부릅니다. | [C4](c-language-features/c4-classmethod.md) |
| staticmethod | `@staticmethod` | `self`도 `cls`도 받지 않는 메서드를 만듭니다. 클래스 안에 둔 일반 함수와 같습니다. | [C5](c-language-features/c5-staticmethod.md) |
| contextmanager | `@contextlib.contextmanager` | `yield` 하나가 있는 함수로 context manager를 만들게 해 줍니다. `yield` 앞이 준비, 뒤가 정리입니다. | [C7](c-language-features/c7-context-manager.md) |
| cache | `@functools.cache` | 같은 인자로 다시 부르면 함수를 실행하지 않고 저장해 둔 결과를 돌려주게 합니다. | [C8](c-language-features/c8-cache.md) |
| class decorator | `@register("name")` 형태 | 클래스 정의 위에 붙여서 클래스를 받아 처리하는 decorator입니다. 등록에 자주 씁니다. | [B3](b-code-structure/b3-registry.md), [C4](c-language-features/c4-classmethod.md) |

## 특수 메서드

Python이 정해진 때에 자동으로 부르는 메서드입니다.

| 메서드 | 불리는 때 | 이 문서에서의 쓰임 | 관련 주제 |
|---|---|---|---|
| `__post_init__` | dataclass가 자동으로 만든 `__init__`이 끝난 직후 | 입력 검사와 정규화 | [C1](c-language-features/c1-dataclass.md) |
| `__init_subclass__` | 하위 클래스가 정의되는 순간 | 하위 클래스 자동 등록 | [C9](c-language-features/c9-init-subclass.md) |
| `__getattr__` | 객체에 없는 속성을 읽으려 할 때 | proxy가 나머지 속성을 원래 객체에 넘김 | [B5](b-code-structure/b5-proxy.md) |
| `__call__` | 객체를 `obj()`처럼 부를 때 | 값을 들고 있는 실행 단위 | [B6](b-code-structure/b6-callable.md) |
| `__enter__`, `__exit__` | `with` 블록에 들어갈 때와 나올 때 | 자원 준비와 정리 | [C7](c-language-features/c7-context-manager.md) |

## 그 밖의 Python 기능

| 용어 | Python 표기 | 설명 | 관련 주제 |
|---|---|---|---|
| context manager | `with` 문 | 블록에 들어갈 때 준비하고, 블록을 나올 때(예외가 나도) 정리하는 객체입니다. | [C7](c-language-features/c7-context-manager.md) |
| BaseException | `BaseException` | 모든 예외의 뿌리입니다. 일반 오류는 그 아래의 `Exception`을 상속합니다. `BaseException`을 직접 상속한 예외는 `except Exception`에 잡히지 않습니다. | [C11](c-language-features/c11-base-exception.md) |
| TYPE_CHECKING | `if typing.TYPE_CHECKING:` | 타입 검사기만 읽고 실행 중에는 건너뛰는 블록입니다. 타입 표기에만 필요한 import를 여기에 둡니다. | [B1](b-code-structure/b1-abc-protocol.md) |
| walrus | `:=` | 값을 변수에 넣으면서 그 값을 바로 식에서 쓰게 하는 연산자입니다. | [C12](c-language-features/c12-small-features.md) |
| keyword-only argument | `def f(a, *, b)` | 함수 정의에서 `*` 뒤에 둔 인자입니다. 호출할 때 반드시 `b=값`처럼 이름을 붙여 넘겨야 합니다. | [C12](c-language-features/c12-small-features.md) |
