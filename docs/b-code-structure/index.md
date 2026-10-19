---
sidebar_position: 0
sidebar_label: "이 절의 주제"
---

# B. 인터페이스와 객체 설계

인터페이스와 구현을 분리하고, 객체의 역할을 나누며, 기능을 추가하거나 교체하는 방법을 다룹니다.

## 주제

- **[B1. ABC와 Protocol](b1-abc-protocol.md)**: interface와 구현을 다른 파일에 두고, 상속은 한두 단계에서 끝내는 방법입니다.
- **[B2. Template method와 hook](b2-template-method.md)**: 하위 클래스가 채우는 `build()`와 바깥에서 부르는 `create()`를 나눠서, 확장 코드의 실수를 경계에서 잡는 방법입니다.
- **[B3. Registry](b3-registry.md)**: 구현을 이름으로 등록하고 이름으로 꺼내 쓰는 방법입니다. 등록할 때 이름 중복과 추상 클래스를 거부합니다.
- **[B4. Mixin](b4-mixin.md)**: 외부 클래스를 고치지 않고, 함께 상속하는 작은 클래스로 기능을 덧붙이는 방법입니다.
- **[B5. Proxy](b5-proxy.md)**: 객체를 감싸서 일부 메서드만 바꾸고, 나머지는 원래 객체에 넘기는 방법입니다.
- **[B6. Callable](b6-callable.md)**: 실행할 동작을 함수, lambda, 호출 가능한 객체로 전달받는 방법입니다.
- **[B7. Context와 상태 객체](b7-context-state.md)**: 단계 사이에 넘기는 값 묶음에서 입력과, 실행 중 바뀌는 상태를 나눠 담는 방법입니다.
