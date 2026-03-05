# 테스트 코드 스타일 (Given/When/Then)

## 1. 기본 원칙

- 모든 테스트는 `Given / When / Then` 주석 블록을 반드시 포함한다.
- 테스트 이름만 보고 실패 의도를 파악할 수 있어야 한다.
- RED 상태의 실패 메시지는 기능 의도를 직접 드러내야 한다.

## 2. 네이밍 규칙

- DisplayName: `[ID] 기대 결과`
- 메서드명: `should_<then>__when_<when>`
- 파일명: `<계층>_<도메인>_<번호>_<주제>Test`

예시:

- DisplayName: `[AT-PC-CORE-01] 입차 성공 시 세션과 점유가 생성된다`
- 메서드명: `should_create_active_session_and_occupancy__when_entry_requested()`
- 파일명: `AT_PC_CORE_01_EntryFlowTest`

## 3. 코드 템플릿 (JUnit5)

```java
@DisplayName("[UT-PC-HIST-01] exit 호출 시 상태가 EXITED로 전이된다")
@Test
void should_mark_exited_and_set_exit_at__when_exit_called() {
    // Given
    ParkingHistory history = ParkingHistory.start(1, 10, "12가3456", now);

    // When
    history.exit(now.plusMinutes(30));

    // Then
    assertThat(history.getStatus()).isEqualTo(EXITED);
    assertThat(history.getExitAt()).isEqualTo(now.plusMinutes(30));
}
```

## 4. 파라미터 테스트 규칙

- 규칙은 같고 입력만 다른 경우 `@ParameterizedTest`로 묶는다.
- 도메인 의미가 다른 케이스는 별도 테스트로 분리한다.
