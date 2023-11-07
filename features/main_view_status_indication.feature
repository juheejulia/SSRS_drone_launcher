@new_gui
Feature: Main View Status Indication

   Status indication is visible on the main view and error message from requests are shown in the status indication.
   Response times are different for different commands due to fixed sleep times in some commands.

   Scenario Outline: Status message is changed to a correct error message after a button is clicked
     Given the launcher is not operational
     And status indication shows an error message
     When <automatic_command> button is clicked
     Then status message shall contain Error during <automatic_command> within 0.1 seconds
     Examples:
       | automatic_command |
       | load              |
       | rest              |
       | prepare           |
       | launch            |
       | stop              |
   
   Scenario Outline: Status message is changed after a button is clicked and launcher is operational
     Given the launcher is operational
     And status indication shows an error message
     When <automatic_command> button is clicked
     Then status indication shall contain <automatic_command> OK within <wait_time> seconds
     Examples:
     | automatic_command   | wait_time      |
     | load                | 2.5            |
     | rest                | 0.5            |
     | prepare             | 0.1            |
     | stop                | 0.1            |

   Scenario: Status message is changed after launch button is clicked and launcher is operational
     Given the launcher is operational
     And launcher is ready to launch
     And status indication shows an error message
     When launch button is clicked
     Then status indication shall contain launch OK within 0.1 seconds

   Scenario: Status message displays OK after launch button is clicked
     Given the launcher is operational
     And launcher is ready to launch
     When launch button is clicked
     Then status indication shall contain launch OK within 0.1 seconds
