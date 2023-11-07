Feature: Automatic positioning commands

  The automatic positioning commands shall move the launcher motors to preconfigured positions.
  The purpose is to simplify the control and also speed up the preparation of a launch.
  Launch command is tested as a separate feature.

  Rule: Errors shall be reported as negative response code with an error message

    Scenario Outline: Error when positioning motors in an automatic mode
    Given <motor> motor is not operational
      When <request> request is posted
      Then negative response code is received
      And error message shall contain motor
      And error message shall contain <request>
    Examples:
      | motor          | request   |
      | drone_position | prepare   |
      | drone_position | stop      |
