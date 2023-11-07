@manual
Feature: Button visibility

  Documentation of non-functional requirements that are not verified with automated test cases.

  Scenario Outline: Visibility outdoor settings
    Given user is on mobile phone in sunny outdoor setting
    When <automatic_command> button is clicked
    Then <automatic_command> button shall be highlighted enough to differentiate from other buttons
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | drone_position      |
    | stop                |
