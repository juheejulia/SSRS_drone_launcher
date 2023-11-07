@new_gui
Feature: Main View Commands

  Landscape tag indicates that scenario is valid in both portrait and landscape mode

  @landscape
  Scenario Outline: Correct buttons are shown in main view
    Given main view is opened
    When user enters the start page
    Then <automatic_command> is shown
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | launch              |
    | stop                |

  Scenario Outline: Buttons highlighted to correct color when clicked
    Given no <automatic_command> has been clicked
    When <automatic_command> button is clicked
    Then <automatic_command> button shall be highlighted
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | launch              |
    | stop                |

  Scenario Outline: Buttons remains highlighted after they have been clicked
    Given <automatic_command> has been clicked
    When one sec has passed
    Then <automatic_command> button shall be highlighted
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | launch              |
    | stop                |

  Scenario Outline: A highlighted button goes back to regular color when the stop button is clicked
    Given <automatic_command> button is highlighted
    When stop button is clicked
    Then <automatic_command> button shall not be highlighted
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | launch              |

  Scenario Outline: A highlighted button is not highlighted after another button is pressed
    Given <automatic_command> button is highlighted
    When <another_automatic_command> button is clicked
    Then <automatic_command> button shall not be highlighted
    Examples:
    | automatic_command   | another_automatic_command |
    | load                | rest                      |
    | rest                | load                      |
    | prepare             | launch                    |
    | launch              | prepare                   |

  @api
  Scenario Outline: Api request is posted when button is clicked
    Given launcher web page is shown
    When <automatic_command> button is clicked
    Then automatic_command api request shall be posted
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | stop                |
    | launch              |

  @api
  Scenario Outline: Correct body message is posted
    Given launcher web page is shown
    When <automatic_command> button is clicked
    Then <automatic_command> command shall be in POST request body
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |

  @skip_mobile
  Scenario Outline: Command button is not highlighted when hovered
    Given launcher web page is shown
    When <automatic_command> is hovered
    Then <automatic_command> button shall not be highlighted
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | launch              |
    | stop                |

  @skip_mobile
  Scenario Outline: Command button is not highlighted when held
    Given launcher web page is shown
    When user holds <automatic_command>
    Then <automatic_command> button shall not be highlighted
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | launch              |
    | stop                |

  Scenario Outline: A highlighted button remains highlighted when the user clicks on it a second time
    Given <automatic_command> button is highlighted
    When <automatic_command> button is clicked
    Then <automatic_command> button shall be highlighted
    Examples:
    | automatic_command   |
    | load                |
    | rest                |
    | prepare             |
    | launch              |

  @landscape
  Scenario: Stop remains visible even if user try to scroll page
    Given stop button is visible
    When user scroll the page
    Then stop is shown

  @landscape
  Scenario: Stop remains visible and have a fixed position even if user try to scroll page
    Given stop button is visible and saves the current position
    When user scroll the page
    Then stop button is still visible and its position is still the same
