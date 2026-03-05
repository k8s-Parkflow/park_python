# 테스트 스위트

## 실행 순서 (TDD)

1. Acceptance (AT)
2. Contract (CT)
3. Unit (UT)
4. Repository/DB (RT, 필요한 경우)

## 작성 규칙

- 테스트 코드는 반드시 `Given / When / Then` 주석 구조를 사용한다.
- 테스트 메서드명은 `should_<then>__when_<when>` 형식으로 작성한다.
- DisplayName은 `[ID] ...` 형식으로 명세 ID와 1:1 매핑한다.

상세 규칙: 'docs/tdd/test-code-style.md'
