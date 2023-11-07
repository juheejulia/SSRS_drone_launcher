@new_gui
Feature: Manual launcher control

    Scenario Outline: Correct manual commands are shown in main view only in portrait
      Given main view is opened
        When user enters the start page
        Then <manual_command> is shown
      Examples:
        | manual_command      |
        | lift                |
        | pitch               |
        | rotation            |
        | case                |
        | drone_position      |


    Scenario Outline: Correct view is opened when manual command is clicked only in portrait
      Given main view is opened
        When <manual_command> button is clicked
        Then <manual_command> window shall be shown
      Examples:
        | manual_command      |
        | pitch               |
        | drone_position      |


    Scenario Outline: Stop button remains visible when manual command view is opened
      Given main view is opened
        When <manual_command> button is clicked
        Then <manual_command> window shall be shown
        And stop button shall be shown
      Examples:
        | manual_command      |
        | pitch               |
        | drone_position      |

    Scenario Outline: Stop button remains possible to interact with when manual command view is opened
      Given <manual_command> window is open
        When stop button is clicked
        Then status indicates stop has been clicked
      Examples:
        | manual_command      |
        | pitch               |
        | drone_position      |


    @new_gui
    Scenario Outline: Main view is shown after exit button is clicked
      Given <manual_command> window is open
        When back arrow button is clicked
        Then <manual_command> is shown
      Examples:
        | manual_command      |
        | pitch               |
        | drone_position      |
       # | lift
       # | direction
       # | case


    Scenario Outline: Status indication is shown when manual command view is open
      Given main view is opened
        And status indication shows an error message
        When <manual_command> button is clicked
        Then manual view status indication shall be visible
      Examples:
        | manual_command      |
        | pitch               |
        | drone_position      |
       # | lift                |
       # | direction           |
       # | case                |


    @api
    Scenario Outline: Motor control movement request body message is posted when clicked
      Given <manual_command> window is open
        When <manual_command>-manual-<direction> button is clicked
        Then <direction> shall be in POST request body
      Examples:
        | manual_command      | direction    |
        | pitch               | up           |
        | pitch               | down         |
        | drone_position      | backward     |
        | drone_position      | forward      |
        # | lift                | up           |
        # | lift                | down         |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

    @api
    Scenario Outline: Motor control movement request body message is posted when held
      Given <manual_command> window is open
        When user holds <manual_command>-manual-<direction>
        Then <direction> shall be in POST request body
      Examples:
        | manual_command      | direction    |
        | pitch               | up           |
        | pitch               | down         |
        # | lift                | up           |
        # | lift                | down         |
        | drone_position      | backward     |
        | drone_position      | forward      |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

   @api
    Scenario Outline: Motor control movement request body message is posted when held and then released
      Given <manual_command> window is open
        When user is holding and then releases <manual_command>-manual-<direction>
        Then stop shall be in POST request body
      Examples:
        | manual_command      | direction    |
        | pitch               | up           |
        | pitch               | down         |
        # | lift                | up           |
        # | lift                | down         |
        | drone_position      | backward     |
        | drone_position      | forward      |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

    @skip_mobile
    @api
    Scenario Outline: Stop command is posted when user holds and then moves cursor away
      Given <motor> window is open
        When user holds <motor>-manual-<direction> and moves cursor away
        Then stop shall be in POST request body
      Examples:
        | motor             | direction    |
        | pitch             | up           |
        | pitch             | down         |
        # | lift                | up           |
        # | lift                | down         |
        | drone_position    | backward     |
        | drone_position    | forward      |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

    Scenario Outline: Motor position is updated when opening manual command view
      Given <motor> is in position 5
        When <motor> button is clicked
        Then <motor> position shall be shown as 5 within 0.1 seconds
      Examples:
        | motor           |
        | pitch           |
        # | lift                |
        | drone_position  |
        # | direction           |
        # | case                |

    Scenario Outline: Manual movement button is not highlighted when clicked and released
      Given <manual_command> window is open
        When user is holding and then releases <manual_command>-manual-<direction>
        Then <manual_command>-manual-<direction> button shall not be highlighted
      Examples:
        | manual_command      | direction     |
        | pitch               | up            |
        | pitch               | down          |
        # | lift                | up           |
        # | lift                | down         |
        | drone_position      | backward      |
        | drone_position      | forward       |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

    Scenario Outline: Manual movement button is highlighted when clicked and held
      Given <manual_command> window is open
        When user holds <manual_command>-manual-<direction>
        Then <manual_command>-manual-<direction> button shall be highlighted
      Examples:
        | manual_command      | direction     |
        | drone_position      | backward      |
        | drone_position      | forward       |
        | pitch               | up            |
        | pitch               | down          |
        # | lift                | up           |
        # | lift                | down         |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

    Scenario Outline: Manual command position is updated after releasing button
      Given <manual_command> window shows position 30
        And <manual_command> is in position 10
        When user is holding and then releases <manual_command>-manual-<direction>
        Then <manual_command> position shall be shown as 10 within 0.5 seconds
      Examples:
        | manual_command      | direction     |
        | pitch               | up            |
        | pitch               | down          |
        # | lift                | up           |
        # | lift                | down         |
        | drone_position      | backward      |
        | drone_position      | forward       |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

    @api
    Scenario Outline: No motor request is made when button is hovered and then moves away
      Given <manual_command> window is open
        When <manual_command>-manual-<direction> is hovered
        And user moves cursor away
        Then motor control request shall not be made
      Examples:
        | manual_command      | direction     |
        | pitch               | up            |
        | pitch               | down          |
        # | lift                | up          |
        # | lift                | down        |
        | drone_position      | backward      |
        | drone_position      | forward       |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

    Scenario Outline: Error message is received after clicking manual movement button
      Given <manual_command> motor is not operational
        And <manual_command> window is open
        When <manual_command>-manual-<movement> button is clicked
        Then status message contains error <manual_command>
      Examples:
        | manual_command      | movement    |
        | pitch               | up          |
        | pitch               | down        |
        # | lift                | up           |
        # | lift                | down         |
        | drone_position      | backward    |
        | drone_position      | forward     |
        # | direction           | left         |
        # | direction           | right        |
        # | case                | open         |
        # | case                | close        |

      Scenario Outline: Correct title is shown in manual command view
      Given main view is opened
        When <manual_command> button is clicked
        Then <manual_command> title is shown at the top of the commands view
      Examples:
        | manual_command      |
        | pitch               |
        | drone_position      |

    Scenario Outline: Set button is enabled after user inputs value
      Given <manual_command> window is open
        When user inputs 100 for drone position
        Then set button shall be enabled
    Examples:
      | manual_command      |
      | drone_position      |

    Scenario Outline: Set button remains disabled when user selects input field
      Given <manual_command> window is open
        When user selects the position input field
        Then set button shall remain disabled
    Examples:
      | manual_command      |
      | drone_position      |

    Scenario: Position input field is shown in the drone-position view
      Given main view is opened
        When drone_position button is clicked
        Then position-input is shown

    Scenario Outline: Invalid drone position shall give an error message
      Given <manual_command> window is open
        When user inputs -5000 for drone position
        And set manual position button is clicked
        Then status indication shall contain <manual_command> motor error within 1.0 seconds
    Examples:
      | manual_command      |
      | drone_position      |

    @api
    Scenario Outline: Motor request shall contain the valid position value
      Given <manual_command> window is open
       When user inputs 100 for drone position
       And set manual position button is clicked
       Then motor request contains the valid 100
    Examples:
      | manual_command      |
      | drone_position      |

     @skip_mobile
     Scenario: Set button is highlighted after valid position is input
       Given user has input a valid drone position
        When user holds set-manual-position-btn
        Then set-manual-position-btn button shall be highlighted

     Scenario: Set button is not highlighted after another input
       Given a valid position has been set
        When user inputs 200 for drone position
        Then set-manual-position-btn button shall not be highlighted

    @manual
    @only_mobile
    Scenario Outline: Mobile keyboard for setting position
      Given <manual_command> window is open
       When user selects the position input field
       Then numeric keyboard shall be shown
    Examples:
      | manual_command      |
      | drone_position      |