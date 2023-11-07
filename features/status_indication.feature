Feature: Status indication

  Status of the different launcher motors shall be indicated to the user, mainly to know if there is
  an error with any of the motors.

  Background:
    Given user is on manual page
  @skip_mobile
    # Test skipped because not functional in mobile view.
  Scenario Outline: Failing to execute a motor command
    Given communication with <motor_interface> is not operational
    When user clicks <motor> <button>
    Then status indication shall contain <motor> motor error within 1.0 seconds
    Examples:
      | motor_interface | motor | button |
      | EPOS            | drone_position | forward |
      | Roboclaw        | pitch  | up |

  Scenario Outline: Error shall be shown in status indication
    Given <motor> motor is not operational
    When user clicks <motor> <button>
    Then status indication shall contain <motor> motor error within 1.0 seconds
      Examples:
      | motor | button |
      | drone_position | forward |
      | case   | open |

  Scenario: Detailed EPOS error message
    Given communication with EPOS is not operational
    When user clicks drone_position forward
    Then status indication shall contain Handle not valid within 1.0 seconds

  Scenario: Status shall show OK when a command has succeeded
    Given drone_position motor is operational
      And status indication shows an error message
    When user clicks drone_position forward
    Then status indication shall contain OK within 1.0 seconds

