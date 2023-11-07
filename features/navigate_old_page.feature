Feature: Navigate to old page

  @new_gui
  Scenario: Navigate from new to old page
    Given main view is opened
    When user navigates to old page
    Then settings page is visible