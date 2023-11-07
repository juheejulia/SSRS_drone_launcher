Feature: Climate control

  Control cooling fans of the launcher and measure/indicate temperature and humidity

  Scenario: Forcing fans active
    Given user is on settings page
    When user clicks force fans
    Then fans are activated

  Scenario: Disabling forced fans
    Given user has forced fans
    When user clicks force fans
    Then fans are controlled based on temperature