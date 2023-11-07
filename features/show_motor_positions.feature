Feature: Show motor positions

  The motor positions shall be indicated around each motor command to allow feedback when
  positioning the motor manually.

  Background:
    Given user is on manual page

  Scenario: Obtaining motor positions with API request
    Given all motors are in position 0
    When measurements request is posted
    Then response code 200 is received
    And response contains all motors at position 0

  Scenario Outline: Motor position shall be updated in the background
    Given all motors are in position 0
    When <motor> moves to position 25
    Then <motor> position shall be shown as 25 within 0.7 seconds
    Examples:
      | motor   |
      | pitch   |
      | drone_position  |
      | lift    |
      | rotation|
      | case1   |
      | case2   |
  @skip_mobile
    # Test skipped because not functional in mobile view.
  Scenario Outline: Position is updated when moving a motor
    # Separate test case to allow testing faster update time when clicking a specific button
    Given all motors are in position 0
      And <motor> will move to position 1
      When user holds <motor> <button>
      Then <motor> position shall be shown as 1 within 0.7 seconds
    Examples:
      | motor   | button      |
      | pitch   | up          |
      | pitch   | down        |
      | drone_position  | backward    |
      | drone_position  | forward     |
      | lift    | up          |
      | lift    | down        |
      | rotation| left        |
      | rotation| right       |
