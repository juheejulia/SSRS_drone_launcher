Feature: Manual launcher control
  Background:
    Given user is on manual page

  Scenario: Request pitch up
   Given server is up
    When pitch up request is posted
    Then positive response code is received

  Scenario Outline: Click motor commands
    Given all motors are operational
      When user clicks <motor> <button>
      Then <motor> <command> is run
      And <motor> is stopped
    Examples:
      | motor   | button      | command           |
      | case    | close       | backward          |
      | case    | open        | forward           |
      | pitch   | up          | backward          |
      | pitch   | down        | forward           |
      | drone_position  | backward    | backward          |
      | drone_position  | forward     | forward           |
      | lift    | up          | forward           |
      | lift    | down        | backward          |
      | rotation| left        | forward           |
      | rotation| right       | backward          |

    Scenario Outline: Click motor min/max commands
    Given all motors are operational
      When user clicks <motor> <button>
      Then <motor> <command> is run
    Examples:
      | motor   | button      | command           |
      | pitch   | min         | move_to_min_position |
      | pitch   | max         | move_to_max_position |
      | lift   | min         | move_to_min_position |
      | lift   | max         | move_to_max_position |

    Scenario Outline: Click motor position commands
    Given all motors are operational
      When user sets desired <motor> position to 1
      And user clicks <motor> position
      Then <motor> move_to_position is run with 1
    Examples:
      | motor   |
      | drone_position  |
      | lift    |

    Scenario Outline: Request motor commands
    Given all motors are operational
      When <motor> <request> request is posted
      Then <motor> <command> is run
    Examples:
      | motor   | request     | command           |
      | pitch   | up          | backward          |
      | pitch   | down        | forward           |
      | drone_position  | backward    | backward          |
      | drone_position  | forward     | forward           |
      | lift    | up          | forward           |
      | lift    | down        | backward          |
      | rotation| left        | forward           |
      | rotation| right       | backward          |
      | case    | close       | backward          |
      | case    | open        | forward           |

    Scenario Outline: Request motor position commands
    Given all motors are operational
      When <motor> position request is posted with position 1
      Then <motor> move_to_position is run
    Examples:
      | motor   |
      | pitch   |
      | drone_position  |
      | lift    |
      | rotation|
      | case    |

  Scenario Outline: Error when positioning motors
    Given <motor> motor is not operational
      When <motor> <request> request is posted
      Then negative response code is received
      And error message shall contain <motor> motor
    Examples:
      | motor   | request   |
      | drone_position  | backward  |
      | drone_position  | forward   |
      | drone_position  | stop      |
      | pitch   | up        |
      | pitch   | down      |
      | pitch   | stop      |
      | case    | open      |
      | case    | close     |
      | case    | stop      |

  Scenario: Negative response when incorrect motor is requested
    Given server is up
    When unsupported backward request is posted
    Then negative response code is received
    And error message shall contain unsupported

  Scenario: Negative response when incorrect motor command is requested
    Given server is up
    When pitch unsupported request is posted
    Then negative response code is received
    And error message shall contain pitch unsupported

  @skip_mobile
    # Test skipped because not functional in mobile view.
  Scenario Outline: Click motor commands and move mouse
    Given all motors are operational
      When user holds <motor> <button> and moves cursor away
      Then <motor> is stopped
    Examples:
      | motor   | button      |
      | case    | close       |
      | case    | open        |
      | pitch   | up          |
      | pitch   | down        |
      | drone_position  | backward    |
      | drone_position  | forward     |
      | lift    | up          |
      | lift    | down        |
      | rotation| left        |
      | rotation| right       |

    Scenario: Click and hold motor commands
    Given all motors are operational
      When user holds rotation left
      Then rotation forward is run

    Scenario Outline: Hover motor commands and move mouse
    Given all motors are operational
    And mouse is on <motor> <button>
      When user moves mouse to status indication
      Then <motor> stop is not run after 0.1 seconds
    Examples:
      | motor   | button      |
      | case    | close       |
      | case    | open        |
      | pitch   | up          |
      | pitch   | down        |
      | drone_position  | backward    |
      | drone_position  | forward     |
      | lift    | up          |
      | lift    | down        |
      | rotation| left        |
      | rotation| right       |