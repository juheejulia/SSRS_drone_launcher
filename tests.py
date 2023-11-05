"""
Step implementations for behave tests
"""
# pylint: disable=no-name-in-module, function-redefined, missing-function-docstring
# no-name-in-module to allow imports of given, when & then.
# function-redefined to not get warnings for each step_impl
# missing-function-docstring since the step name shall be descriptive (no need for doc string)
import time
from ctypes import c_uint
from unittest.mock import Mock, call
import ast

from nose.tools import assert_equal, assert_true, assert_not_equal, assert_in
import selenium.common
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.color import Color
from features.environment import mock_epos_interface, APP_URL, APP_URL_OLD, AUTOMATIC_COMMAND_URL,\
    MOTOR_CONTROL_URL
from models.launcher_model import create_motor_list, NotReadyException
from controls.launcher_control import LauncherControl

AUTOMATIC_COMMANDS = LauncherControl.AUTOMATIC_COMMANDS
MOCKED_MOTOR_COMMANDS = ["forward", "backward", "stop", "move_to_position"]
BUTTON_PRIMARY_COLOR = "#FCE0CF"
MANUAL_BUTTON_PRIMARY_COLOR = "#FFFBFA"
BUTTON_ACTIVE_COLOR = "#F7AE82"
BUTTON_PRIMARY_COLOR_STOP = "#E54A3B"
BUTTON_ACTIVE_COLOR_STOP = "#9E2114"
SET_BUTTON_PRIMARY_COLOR = "#FFFBFA"
STANDARD_WAIT_TIME = 1
STANDARD_ERROR_MESSAGE = "An error has occurred"
SELENIUM_WIRE_WAIT_TIME = 15
CLOSE_MANUAL_VIEW = "close-manual-view"
MANUAL_VIEW_STATUS_MESSAGE = "manual-status-indication__message"
MANUAL_VIEW_STATUS_TITLE = "manual-status-indication__title"
MAIN_VIEW_STATUS_MESSAGE = "status-indication__message"
MOTOR_POSITION = "motor-position"
MANUAL_COMMAND_TITLE = "manual-command-title"
VALID_DRONE_POSITION = "100"
SET_BUTTON = "set-manual-position-btn"
DRONE_POSITION = "manual-position-input"

# Default value for sleep interval between evaluation calls, used when waiting for elements or text
# to be present
ELEMENT_POLL_FREQUENCY = 0.1


@given('user has prepared for a launch')
def step_impl(context):
    context.execute_steps("""Given user is on automatic page
    And all motors are operational
    And launcher is ready to launch
    """)


@given('server is up')
def step_impl(context):
    context.browser.find_element(By.XPATH, '//button[@id="script_pitch_up"]')


@given('user has forced fans')
def step_impl(context):
    context.execute_steps("""Given user is on settings page
        When user clicks force fans""")


@given('user is on automatic page')
def step_impl(context):
    go_to_page(context, "automatic")
    wait_until_page_contains_element(context, "automatic_position_buttons", STANDARD_WAIT_TIME)


@given('user is on manual page')
def step_impl(context):
    go_to_page(context, "manual")
    wait_until_page_contains_element(context, "script_pitch_up", STANDARD_WAIT_TIME)


@given('user is on settings page')
def step_impl(context):
    go_to_page(context, "settings")
    wait_until_page_contains_element(context, "script_force_fans", STANDARD_WAIT_TIME)


def go_to_page(context, page):
    button_element = find_element(context, f"{page}_page")
    button_element.click()


@given('the launcher is {operational}')
def step_impl(context, operational):
    context.execute_steps("Given main view is opened")
    if operational == "operational":
        set_all_motors_operational(context)
    elif operational == "not operational":
        set_all_motors_not_operational(context)


@given('all motors are operational')
def set_all_motors_operational(context):
    # Mock all motors to be able to assert that the correct motor function calls has been made
    # Launch motor will be restored to non mocked version in before_scenario
    for name, motor in context.launcher.motors.items():
        context.launcher.motors[name] = Mock(motor)
        context.launcher.motors[name].get_actual_position = Mock(return_value=0)


@given('all motors are not operational')
def set_all_motors_not_operational(context):
    for motor_name in context.launcher.motors.keys():
        set_motor_operational(context, motor_name, "not operational")


@given('{motor} motor is {operational}')
def set_motor_operational(context, motor, operational):
    motor = motor.lower()
    operational = operational.lower()
    if motor == "drone_position":
        if operational == "operational":
            low_level_return_value = 1
            context.epos.epos.error_code = c_uint(0)
        elif operational == "not operational":
            # Make all low level CDLL calls return 0 so that this step will produce an error for all
            # functions related to the drone_position motor
            low_level_return_value = 0
        else:
            raise ValueError("Incorrect value for provided 'operational'")

        mock_epos_interface(context.epos.epos, low_level_return_value)
    else:
        if operational.lower() == "not operational":
            mock_motor_commands_error(context, motor)


@given('communication with {motor_interface} is not operational')
def step_impl(context, motor_interface):
    # Remove mocks for all motor so that low level calls will be performed and produce errors
    for name in context.launcher.motors.keys():
        context.launcher.motors[name] = context.non_mocked_motors[name]

    # Create a non-working communication by re-opening communication with a faulty port name
    if motor_interface.lower() == "roboclaw":
        context.roboclaw.comport = ""
        try:
            context.roboclaw.Open()
        except IOError:
            pass
    elif motor_interface.lower() == "epos":
        # Remove all low level mocks so that the error can be shown
        mock_epos_interface(context.epos.epos, return_value=0)

        # Set an error code to indicate the error present when no EPOS is connected
        context.epos.error_code = c_uint(268435459)
        context.epos.port = ""
        try:
            context.epos.open()
        except IOError:
            pass
    else:
        raise ValueError("Incorrect value for motor_interface!")


@given('launcher is {status} to launch')
def step_impl(context, status):
    if status == "ready":
        context.launcher.assert_ready_to_launch = Mock()

        # Mock waiting to prevent timeout and IOError
        context.launcher.motors['drone_position'].wait_until_motor_stopped = Mock()
        context.launcher.motors['drone_position'].set_charger_state = Mock()
    elif status == "not ready":
        context.launcher.assert_ready_to_launch = Mock(side_effect=NotReadyException)
    else:
        raise ValueError("Incorrect value for launcher status!")


@given('a launch has been performed')
def step_impl(context):
    context.launcher.ready_to_launch = True
    post_request(context, "launch")


@given('an error occurred during launch')
def step_impl(context):
    context.launcher.ready_to_launch = True
    # Make an error occur during launch
    mock_epos_interface(context.epos.epos, 0)
    post_request(context, "launch")


@given('status indication shows an error message')
def step_impl(context):
    if "/old" in context.browser.current_url:
        # set internal status (used for old GUI)
        context.launcher.set_status_message(STANDARD_ERROR_MESSAGE)
    else:
        # set a status in both status message fields in new GUI
        status_message_elements = [MANUAL_VIEW_STATUS_MESSAGE, MAIN_VIEW_STATUS_MESSAGE]
        for element in status_message_elements:
            context.browser.execute_script(f"document.getElementById('{element}')."
                                           f"textContent='{STANDARD_ERROR_MESSAGE}'")

    # Ensure that the error message is visible
    context.execute_steps(f"Then status indication shall "
                          f"contain {STANDARD_ERROR_MESSAGE} "
                          f"within {STANDARD_WAIT_TIME:.1f} seconds")


@given('{manual_command} window shows position {value}')
def step_impl(context, manual_command, value):
    context.execute_steps(f"""Given {manual_command} window is open""")
    context.browser.execute_script(f"document.getElementById('{MOTOR_POSITION}')."
                                   f"textContent='{value}'")

    # Ensure that the manual_command position is visible
    wait_until_text_present_in_element(context, MOTOR_POSITION,
                                       f'{value}', STANDARD_WAIT_TIME)


@given('all motors are in position {position:d}')
def step_impl(context, position):
    for motor in context.launcher.motors:
        mock_motor_position(context, motor, position)


@given('{motor} will move to position {position:d}')
def step_impl(context, motor, position):
    mock_motor_position(context, motor, position)


@given('{motor} is in position {position}')
def step_impl(context, motor, position):
    mock_motor_position(context, motor, position)


@given('main view is opened')
def step_impl(context):
    if context.browser:
        pass


@given('no {automatic_command} has been clicked')
def step_impl(context, automatic_command):
    context.execute_steps("""When user enters the start page""")
    if automatic_command == "stop":
        button_expected_color = BUTTON_PRIMARY_COLOR_STOP
    else:
        button_expected_color = BUTTON_PRIMARY_COLOR
    verify_button_has_color(context, automatic_command, button_expected_color)


@given('{automatic_command} has been clicked')
def step_impl(context, automatic_command):
    context.execute_steps("""When user enters the start page""")
    button_element = context.browser.find_element(By.ID, f"{automatic_command}-btn")
    button_element.click()


@given('{automatic_command} button is highlighted')
def step_impl(context, automatic_command):
    context.execute_steps(f"""Given {automatic_command} has been clicked
    Then {automatic_command} button shall be highlighted""")


@given('launcher web page is shown')
def step_impl(context):
    context.execute_steps("""When user enters the start page""")


@given('stop button is visible')
def step_impl(context):
    context.execute_steps("""When user enters the start page""")
    wait_until_page_contains_element(context, "stop-btn", STANDARD_WAIT_TIME)


@given('stop button is visible and saves the current position')
def step_impl(context):
    context.execute_steps("""When user enters the start page""")
    wait_until_page_contains_element(context, "stop-btn", STANDARD_WAIT_TIME)
    button_position = context.browser.find_element(By.ID, "stop-btn")
    context.start_location = button_position.location


@given('mouse is on {button}')
def step_impl(context, button):
    button_id = "script_" + button.replace(" ", "_")
    button_element = context.browser.find_element(By.ID, button_id)
    ActionChains(context.browser).move_to_element(button_element).perform()


@given('{manual_command} window is open')
def step_impl(context, manual_command):
    context.execute_steps(f"""Given main view is opened
                            Then {manual_command} button shall be shown
                            When {manual_command} button is clicked
                            Then {manual_command} window shall be shown""")


@given('user has input a valid drone position')
def step_impl(context):
    context.execute_steps("""Given drone_position window is open
                            When user inputs 50 for drone position
                            Then set button shall be enabled""")


@given('a valid position has been set')
def step_impl(context):
    context.execute_steps("Given user has input a valid drone position")
    click_button(context, SET_BUTTON)


@when('measurements request is posted')
def step_impl(context):
    context.response = context.server.get_app().test_client().get("/measurements")


@when('user enters the start page')
def step_impl(context):
    # Only load the page if necessary
    if context.browser.current_url != APP_URL:
        context.browser.get(url=APP_URL)


@when('{motor} moves to position {position}')
def step_impl(context, motor, position):
    mock_motor_position(context, motor, position)


@when('user clicks {button}')
def step_impl(context, button):
    button_id = "script_" + button.replace(" ", "_")
    button_element = find_element(context, button_id)
    button_element.click()


@when('back arrow button is clicked')
def step_impl(context):
    click_button(context, CLOSE_MANUAL_VIEW)


@when('set {manual_command} position button is clicked')
def step_impl(context, manual_command):
    click_button(context, f"set-{manual_command}-position-btn")


@when('user sets desired {motor} position to {position:d}')
def step_impl(context, motor, position):
    if motor.endswith("_position"):
        motor = motor[0:-9]
    position_element = find_element(context, f"{motor}_position")
    position_element.send_keys(position)


@when('user holds {button} and moves cursor away')
def step_impl(context, button):
    for status_indication_id in ["status_indication", "status-indication__message"]:
        try:
            context.browser.find_element(By.ID, status_indication_id)
            element_name = status_indication_id
            break
        except selenium.common.exceptions.NoSuchElementException:
            element_name = None

    if element_name is None:
        raise selenium.common.exceptions.NoSuchElementException("No status indication element")

    if element_name == "status_indication":
        button_element = find_element(context, "script_" + button)
    else:
        button_element = find_element(context, button)

    actions = ActionChains(context.browser)
    actions.click_and_hold(button_element)
    actions.perform()
    # Move the cursor away from element
    move_cursor_away(context)


@when('user holds {button}')
def step_impl(context, button):
    # Checks if test is run on URL for old or new page as element IDs are named differently.
    if context.browser.current_url == APP_URL:
        button_element = find_element(context, button)
    else:
        button_element = find_element(context, "script_" + button)
    actions = ActionChains(context.browser)
    actions.click_and_hold(button_element).perform()


@when('user is holding and then releases {button}')
def hold_and_release_button(context, button):
    button_element = find_element(context, button)
    actions = ActionChains(context.browser)
    actions.click_and_hold(button_element)
    actions.release(button_element)
    actions.perform()


@when('{motor} {command} request is posted')
def step_impl(context, motor, command):
    parameters = {"motor": motor.lower(), "command": command.lower()}
    post_request(context, "motor_control", parameters)


@when('{motor} position request is posted with position {position:d}')
def step_impl(context, motor, position):
    parameters = {"motor": motor.lower(), "command": "position", "position": position}
    post_request(context, "motor_control", parameters)


@when('{command} request is posted')
def step_impl(context, command):
    if command in AUTOMATIC_COMMANDS:
        post_request(context, "automatic_command", {"command": command}, True)
    else:
        post_request(context, command.lower())


@when('{command} button is clicked')
def click_button(context, command):
    # Use hold and release instead of just click to prevent issues with request logging in
    # selenium-wire. When click is used for manual motor control, POST requests for motor
    # and the consecutive stop can be logged in incorrect order. Probably due to the short
    # time between button down and up.
    hold_and_release_button(context, command)


@when('one sec has passed')
def step_impl(context):
    if context.browser:
        time.sleep(1)


@when('{button} is hovered')
def step_impl(context, button):
    button_element = find_element(context, button)
    actions = ActionChains(context.browser)
    actions.move_to_element(button_element).perform()


@when('user moves cursor away')
def move_cursor_away(context):
    actions = ActionChains(context.browser)
    # Move the cursor away from element
    actions.move_by_offset(100, 100)
    actions.perform()


@when('user navigates to old page')
def step_impl(context):
    context.browser.get(url=APP_URL_OLD)


@when('user scroll the page')
def step_impl(context):
    context.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")


@when('user moves mouse to {element}')
def step_impl(context, element):
    # now works for both buttons and status indication
    if element == "status indication":
        element_id = element
    else:
        element_id = "script_" + element
    gui_element = find_element(context, element_id)
    actions = ActionChains(context.browser)
    actions.move_to_element(gui_element).perform()


@when('user inputs {value} for drone position')
def step_impl(context, value):
    input_field = find_element(context, DRONE_POSITION)
    input_field.send_keys(value)


@when('user selects the position input field')
def step_impl(context):
    click_button(context, DRONE_POSITION)


@then('positive response code is received')
def step_impl(context):
    print("Response code: " + str(context.response.status_code))
    assert_equal(context.response.status_code, 200)


@then('response code {code} is received')
def step_impl(context, code):
    print("Response code: " + str(context.response.status_code))
    assert_equal(context.response.status_code, int(code))


@then('negative response code is received')
def step_impl(context):
    response_code = context.response.status_code
    print("Response code: " + str(response_code))
    assert_in(response_code, (400, 404))


@then('status message contains error {error_message}')
def step_impl(context, error_message):
    wait_until_text_present_in_element(context, MANUAL_VIEW_STATUS_MESSAGE,
                                       error_message.capitalize(), SELENIUM_WIRE_WAIT_TIME)


@then('error message shall contain {error_text}')
def step_impl(context, error_text):
    message = str(context.response.data)
    print("Error message: " + message)
    for substring in error_text.lower().split(" "):
        assert_in(substring, message.lower())


@then('{motor} {command} is run')
def step_impl(context, motor, command):
    motor_list = create_motor_list(motor)
    for motor_name in motor_list:
        assert_motor_command_called_once(context, command, motor_name)


@then('{motor} {command} is run with {position:d}')
def step_impl(context, motor, command, position):
    motor_list = create_motor_list(motor)
    for motor_name in motor_list:
        assert_motor_command_called_once(context, command, motor_name, position)


@then('{motor} is stopped')
def step_impl(context, motor):
    motor_list = create_motor_list(motor)
    for motor_name in motor_list:
        assert_motor_command_called_once(context, "stop", motor_name)


@then('response contains all motors at position {position:d}')
def step_impl(context, position):
    response_keys = context.response.json.keys()

    # Save the motor position keys, since the response contains more data than positions
    motor_pos_keys = []

    # Verify that all expected positions are part of the response
    for motor_expected in context.launcher.motors:
        motor_pos_key = motor_expected + "_pos"
        assert_in(motor_pos_key, response_keys)
        motor_pos_keys.append(motor_pos_key)

    # Verify that all positions are as expected
    for key in motor_pos_keys:
        position_actual = context.response.json[key]
        assert_equal(position_actual, position)


@then('response contains {message_text}')
def step_impl(context, message_text):
    complete_response = context.response.json
    assert_in("status", complete_response.keys())
    status_message = complete_response["status"]
    for expected_message_part in message_text.split(" "):
        assert_in(expected_message_part.lower(), status_message.lower())


@then('{motor} position shall be shown as {position} within {response_time:f} seconds')
def step_impl(context, motor, position, response_time):
    if context.browser.current_url == APP_URL_OLD:
        position_element_name = motor + "_pos"
    else:
        position_element_name = MOTOR_POSITION
    wait_until_text_present_in_element(context, position_element_name, position, response_time)


@then('status indication shall contain {message} within {response_time:f} seconds')
def step_impl(context, message, response_time):
    # Checks for which status indication id to use
    element_name = None
    for status_indication_id in ["status_indication", "status-indication__message",
                                 "manual-status-indication__message"]:
        try:
            element = context.browser.find_element(By.ID, status_indication_id)
            # Check isDisplayed to not use a hidden status element
            if element.is_displayed():
                element_name = status_indication_id
                break
        except selenium.common.exceptions.NoSuchElementException:
            element_name = None

    if element_name is None:
        raise selenium.common.exceptions.NoSuchElementException("No status indication element")

    # Handle evaluation of different kind of status messages
    if message == "OK":
        pass
    elif " OK" in message:
        # Capitalize first letter in message to match the status indication, e.g. Pitch OK
        message = message.split()[0].capitalize() + " OK"
    else:
        # Since the wait until is case-sensitive, make first letter capital to find error message
        # based on variables used in scenario examples that are lower case
        message = message.capitalize()

    wait_until_text_present_in_element(context, element_name, message, response_time)


@then('fans are activated')
def step_impl(context):
    wait_for_request()
    assert_equal(context.launcher.climate_control.activate_fans.mock_calls[-1], call(True))


@then('{command} is shown')
def step_impl(context, command):
    if command not in DRONE_POSITION:
        wait_until_page_contains_element(context, f"{command}-btn", STANDARD_WAIT_TIME)
    else:
        wait_until_page_contains_element(context, DRONE_POSITION, STANDARD_WAIT_TIME)


@then('fans are controlled based on temperature')
def step_impl(context):
    # Verify by asserting that the fan control is updated, don't care about the actual argument
    wait_for_request()
    assert_equal(context.launcher.climate_control.activate_fans.mock_calls[-1], call(False))


@then('{command} button shall be highlighted')
def step_impl(context, command):
    if command == "stop":
        button_expected_color = BUTTON_ACTIVE_COLOR_STOP
    else:
        button_expected_color = BUTTON_ACTIVE_COLOR
    wait_until_element_has_color(context, command, button_expected_color, STANDARD_WAIT_TIME)


@then('{command} button shall not be highlighted')
def step_impl(context, command):
    if command == "stop":
        button_expected_color = BUTTON_PRIMARY_COLOR_STOP
    elif "manual" in command:
        button_expected_color = MANUAL_BUTTON_PRIMARY_COLOR
    elif "set" in command:
        button_expected_color = SET_BUTTON_PRIMARY_COLOR
    else:
        button_expected_color = BUTTON_PRIMARY_COLOR
    wait_until_element_has_color(context, command, button_expected_color, STANDARD_WAIT_TIME)


def verify_button_has_color(context, automatic_command, button_expected_color):
    button_actual_color = get_button_color(context, automatic_command)
    assert_equal(button_expected_color, button_actual_color,
                 f"Actual color {button_actual_color} doesn't match "f"{button_expected_color}")


@then('{automatic_command} api request shall be posted')
def step_impl(context, automatic_command):
    command_url = f"{APP_URL}app_{automatic_command}"
    context.browser.wait_for_request(command_url,
                                     timeout=SELENIUM_WIRE_WAIT_TIME)
    driver_request = context.browser.last_request.url
    assert_equal(driver_request, command_url)


@then('settings page is visible')
def step_impl(context):
    wait_until_page_contains_element(context, "settings_page", STANDARD_WAIT_TIME)


@then('stop button is still visible and its position is still the same')
def step_impl(context):
    wait_until_page_contains_element(context, "stop-btn", STANDARD_WAIT_TIME)
    button_position = context.browser.find_element(By.ID, "stop-btn")
    assert_equal(button_position.location, context.start_location)


@then('{automatic_command} command shall be in POST request body')
def step_impl(context, automatic_command):
    context.browser.wait_for_request(AUTOMATIC_COMMAND_URL, timeout=SELENIUM_WIRE_WAIT_TIME)
    # Get body from last request and convert from byte to dict
    driver_request_body = ast.literal_eval(context.browser.last_request.body.decode("utf-8"))
    assert_equal(driver_request_body["command"], automatic_command)


@then('{command} shall be in POST request body')
def step_impl(context, command):
    request_evaluate = context.browser.wait_for_request(MOTOR_CONTROL_URL,
                                                        timeout=SELENIUM_WIRE_WAIT_TIME)
    # Short wait to allow catching consecutive requests to aid in troubleshooting
    time.sleep(0.1)
    # When clicking, both motor command and stop requests are sent.
    # The stop request will be the last motor_control request when re-fetching the request list
    request_list = context.browser.requests
    if command == "stop":
        # The request list is expected to contain the motor command, stop and get_measurements
        # Evaluate the last three elements in case of stop being sent before motor command
        # List in reversed order so that the stop request will be the first motor_control request
        for request in reversed(request_list[-3:]):
            if "motor_control" in request.path:
                request_evaluate = request
                break
    # Decode the request to verify the command
    request_body = ast.literal_eval(request_evaluate.body.decode("utf-8"))
    actual_command = request_body["command"]

    # Create a list of all request bodies to provide a better error message
    request_body_list = [x.body for x in request_list if "app_motor_control" in x.url]
    assert_equal(command, actual_command, f"Actual command '{actual_command}' did not match "
                                          f"'{command}'. Requests: {request_body_list}")


@then('status message shall contain Error during {automatic_command} '
      'within {response_time:f} seconds')
def step_impl(context, automatic_command, response_time):
    element_name = "status-indication__message"
    wait_until_text_present_in_element(context, element_name,
                                       f"Error during {automatic_command}", response_time)


@then('{motor} {command} is not run after {wait_time:f} seconds')
def step_impl(context, motor, command, wait_time):
    motor_list = create_motor_list(motor)
    for motor_name in motor_list:
        expected_call = getattr(context.launcher.motors[motor_name], command)
        time.sleep(wait_time)
        expected_call.assert_not_called()


@then('{command} button shall be shown')
def step_impl(context, command):
    wait_until_page_contains_element(context, f"{command}-btn", STANDARD_WAIT_TIME)


@then('{manual_command} window shall be shown')
def step_impl(context, manual_command):
    # Check correct name to get from attribute.
    element = context.browser.find_element(By.ID, "manual-command-view")
    # # Converts attribute str to bool. Will have attribute with "true" if window opened
    assert_true(bool(element.get_attribute("data-manual-command-view-opened")))

    wait_until_manual_command_title_is_shown(context, manual_command)


@then('status indicates {command} has been clicked')
def step_impl(context, command):
    status_text = context.browser.find_element(By.ID, MANUAL_VIEW_STATUS_MESSAGE).text
    if f"{command} OK" in status_text:
        # Capitalize first letter as command in status message will be capitalized.
        command = status_text.split()[0].capitalize() + " OK"
        wait_until_text_present_in_element(context, MANUAL_VIEW_STATUS_MESSAGE,
                                           command, STANDARD_WAIT_TIME)


@then('manual view status indication shall be visible')
def wait_until_manual_status_visible(context):
    wait = WebDriverWait(context.browser, STANDARD_WAIT_TIME, poll_frequency=ELEMENT_POLL_FREQUENCY)
    wait.until(EC.visibility_of_element_located((By.ID, MANUAL_VIEW_STATUS_TITLE)))
    wait.until(EC.visibility_of_element_located((By.ID, MANUAL_VIEW_STATUS_MESSAGE)))


@then('motor control request shall not be made')
def step_impl(context):
    # Captures all requests in a list
    request_list = context.browser.requests

    # Verifies no request is a motor control request
    for request in request_list:
        assert_not_equal(str(request), MOTOR_CONTROL_URL)


@then('{manual_command} title is shown at the top of the commands view')
def wait_until_manual_command_title_is_shown(context, manual_command):
    element_title = manual_command.replace("_", " ").title()
    wait_until_text_present_in_element(context, MANUAL_COMMAND_TITLE, element_title,
                                       STANDARD_WAIT_TIME)


@then('set button shall be enabled')
def step_impl(context):
    assert_button_enabled(context, SET_BUTTON)


@then('set button shall remain disabled')
def step_impl(context):
    assert_button_enabled(context, SET_BUTTON, enabled=False)


@then('motor request contains the valid {value}')
def step_impl(context, value):
    context.browser.wait_for_request(MOTOR_CONTROL_URL, timeout=SELENIUM_WIRE_WAIT_TIME)
    # Get body from last request and convert from byte to dict
    driver_request_body = ast.literal_eval(context.browser.last_request.body.decode("utf-8"))
    assert_equal(driver_request_body['position'], value,
                 f"Actual value: {driver_request_body['position']}"
                 f" did not match Expected value: {value}")


def post_request(context, complete_command, parameters=None, use_json=False):
    """
    Helper function to post a request to the API.
    @param context: context from behave.
    @param complete_command: the request to be posted.
    @param parameters: dictionary to be added as data for the request.
    @param use_json: boolean indicating if request body is sent as json or not."""
    # Utilize the app instance that was set up in the environment
    request = f"/app_{complete_command}"
    if use_json:
        response = context.server.get_app().test_client().post(request, json=parameters)
    else:
        response = context.server.get_app().test_client().post(request, data=parameters)

    context.response = response
    return response


def assert_motor_command_called_once(context, command, motor, argument=None):
    """Asserts that a specified command has been called for a mocked motor."""
    # Need some time for the function to be called
    wait_for_request()
    # Utilize the mocked motor to verify correct function call
    expected_call = getattr(context.launcher.motors[motor], command)

    if argument:
        expected_call.assert_called_once_with(argument)
    else:
        expected_call.assert_called_once()


def assert_button_enabled(context, button, enabled=True):
    button_element = find_element(context, button)
    assert_equal(enabled, button_element.is_enabled())


def wait_for_request():
    time.sleep(0.5)


def mock_motor_position(context, motor, position):
    # Handle the case position by mocking the position of both motors
    if motor == "case":
        motor_list = ["case1", "case2"]
    else:
        motor_list = [motor]

    for motor_name in motor_list:
        context.launcher.motors[motor_name].get_actual_position = Mock(return_value=position)


def find_element(context, element):
    if context.browser.current_url == APP_URL:
        # Used to separate motor control command ID from automatic commands
        # Example: pitch-btn from pitch-manual-up which needs "-btn" ending added in argument
        if '-' in element:
            button_element = context.browser.find_element(By.ID, element)
        else:
            button_element = context.browser.find_element(By.ID, f"{element}-btn")
    else:
        # Handle if the requested button has a whitespace
        element_id = element.replace(" ", "_")
        button_element = context.browser.find_element(By.ID, element_id)
    return button_element


def get_button_color(context, button):
    """Locates and returns element hex color as string"""
    button_element = find_element(context, button)
    button_rgba = button_element.value_of_css_property("background-color")
    return Color.from_string(button_rgba).hex.upper()


def mock_motor_commands_error(context, motor):
    error_mock = Mock(side_effect=IOError)
    # Handle the case position by mocking the position of both motors
    if motor == "case":
        motor_list = ["case1", "case2"]
    else:
        motor_list = [motor]

    for motor_name in motor_list:
        for command in MOCKED_MOTOR_COMMANDS:
            setattr(context.launcher.motors[motor_name], command, error_mock)


def wait_until_text_present_in_element(context, element_name, expected_text, response_time):
    """
    Waits until the expected text is present in the element.
    Adds the element text to the exception message to provide troubleshooting-info.
    This can be a different text than the one evaluated by wait-until if the element text
    has changed between the wait-until evaluation and retrieving the text for the timeout message
    :param context: Context with webdriver
    :param element_name: ID of the element to be evaluated
    :param expected_text: String with the text that is expected to be present
    :param response_time: Time in seconds to wait for the text to be present
    """
    wait = WebDriverWait(context.browser, response_time, poll_frequency=ELEMENT_POLL_FREQUENCY)
    try:
        wait.until(EC.text_to_be_present_in_element((By.ID, element_name), expected_text))
    except selenium.common.exceptions.TimeoutException as err:
        element_text = context.browser.find_element(By.ID, element_name).text
        err.msg = f'Element "{element_name}" was expected to contain "{expected_text}"' \
                  f' but has text after the timeout occurred: "{element_text}"'
        raise err


def wait_until_page_contains_element(context, element_name, response_time):
    wait = WebDriverWait(context.browser, response_time, poll_frequency=ELEMENT_POLL_FREQUENCY)
    wait.until(EC.visibility_of_element_located((By.ID, element_name)))


def wait_until_element_has_color(context, element_name, expected_color, response_time):
    wait = WebDriverWait(context.browser, response_time, poll_frequency=ELEMENT_POLL_FREQUENCY)
    element = find_element(context, element_name)
    timeout_message = f"Element '{element_name}' did not have expected color: {expected_color}."
    wait.until(element_has_color(element, expected_color), message=timeout_message)


def element_has_color(element, expected_color):
    """
    An expectation for checking that an element has a particular css class.

      :param element: element which is expected to have the color
      :param expected_color: String with expected color in hex format
      returns the WebElement once it has the expected color
      """

    def _predicate(_):
        button_rgba = element.value_of_css_property("background-color")
        actual_color = Color.from_string(button_rgba).hex.upper()
        if expected_color == actual_color:
            return element
        return False

    return _predicate
