Feature: Launch Drone

  Scenario: Ready to launch
    Given launcher is ready to launch
      When launch request is posted
      Then positive response code is received

  Scenario: Launch button moves drone_position motor
    Given user has prepared for a launch
      When user clicks launch
      Then drone_position move_to_launch_position is run

  Scenario: Error when launching drone
    Given drone_position motor is not operational
    And launcher is ready to launch
      When launch request is posted
      Then negative response code is received
      And error message shall contain launch motor

  Scenario: Not ready to launch
    Given launcher is not ready to launch
      When launch request is posted
      Then negative response code is received
      And error message shall contain not ready

  Scenario: Not ready after error
    Given an error occurred during launch
      When launch request is posted
      Then negative response code is received
      And error message shall contain not ready

  Scenario: Consecutive launches need preparation
    Given a launch has been performed
      When launch request is posted
      Then negative response code is received
      And error message shall contain not ready
