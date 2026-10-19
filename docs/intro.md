---
slug: "/"
sidebar_position: 1
sidebar_label: "개요"
---

# Self-Index에서 배울 수 있는 설계 지식

**이 문서의 출발점은 [augustinLib/Self-Index](https://github.com/augustinLib/Self-Index)입니다.
원본 코드와 설계의 크레딧은 Self-Index 저자와 기여자에게 있습니다.**

Self-Index의 [commit `9c6fade`](https://github.com/augustinLib/Self-Index/tree/9c6fade)를 분석해,
다른 프로젝트에서도 참고할 수 있는 설계 지식을 정리했습니다. 설명용 예시와 적용 규칙은 이 학습 노트에서
정리한 내용이며, 실제 레포 코드와 구분해 표시했습니다.

[코딩 규약](./coding-convention.md)은 적용할 규칙을, 이 문서는 그 의미와 이유를 설명합니다.
통계와 코드 위치를 기록한 [분석 원본](https://github.com/happysnail06/code-design-note/blob/main/sources/self-index-coding-conventions.md)도 함께 제공합니다.

문서는 다음 순서로 되어 있습니다.

1. **먼저 알아 둘 개념**: 이 문서에 나오는 용어를 묶음별로 설명합니다.
2. **한눈에 보기**: 모든 주제를 한 줄 설명과 함께 모았습니다.
3. **상세 분석**: 주제마다 하나씩 정리했습니다. 각 주제는 이름과 한 문장 설명으로 시작하고, 다음 절이
   이어집니다. 해당하지 않는 절은 생략했습니다.
   - **개념**: 이 주제의 핵심 개념입니다.
   - **사용 방법**: 무엇을 어떻게 하는지입니다.
   - **왜 필요한가**: 그렇게 하면 어떤 문제가 없어지는지입니다.
   - **예시**: 레포와 상관없이 이해할 수 있게 만든 작은 Python 코드입니다. `# 예시`로 시작하는 코드는 모두
     실제로 실행해서 확인했습니다.
   - **Self-Index에서의 사용**: 레포의 실제 코드 발췌와 위치(`파일:줄`)입니다. 줄인 곳은 `...`로
     표시했습니다.
   - **주의할 점**: 이 방법이 맞지 않는 상황과 한계입니다.
