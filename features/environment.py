"""Prepares the test environment for the web application."""
# Python standard imports (according to Pylint)
import threading
import copy
from wsgiref import simple_server
from wsgiref.simple_server import WSGIRequestHandler
from unittest.mock import MagicMock, Mock

# Other imports (not standard according to Pylint)
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver import ActionChains
from seleniumwire import webdriver as wire_webdriver
from main import initialize_system

chrome_options = Options()
chrome_options.add_argument("--headless")
# Set the window size to ensure all elements are possible to interact with
chrome_options.add_argument("window-size=1920,1080")
# Uses the no-sandbox option as a workaround for Chrome crashing when run as root in docker
# container on Jenkins.
chrome_options.add_argument("--no-sandbox")

mocked_epos_dll_methods = ["VCS_OpenDevice", "VCS_SetEnableState", "VCS_MoveWithVelocity",
                           "VCS_ActivateProfileVelocityMode", "VCS_SetVelocityProfile",
                           "VCS_SetMaxProfileVelocity", "VCS_HaltVelocityMovement",
                           "VCS_ActivateProfilePositionMode", "VCS_SetPositionProfile",
                           "VCS_HaltPositionMovement", "VCS_MoveToPosition",
                           "VCS_ActivateHomingMode", "VCS_SetHomingParameter", "VCS_FindHome",
                           "VCS_StopHoming", "VCS_WaitForHomingAttained",
                           "VCS_SetAllDigitalOutputs", "VCS_SetQuickStopState"]

APP_PORT = 5000
APP_URL = f"http://localhost:{APP_PORT}/"
APP_URL_OLD = f"{APP_URL}old"
AUTOMATIC_COMMAND_URL = f"{APP_URL}app_automatic_command"
MOTOR_CONTROL_URL = f"{APP_URL}app_motor_control"

# Default iPhone 11 device metrics
MOBILE_SCREEN_WIDTH = 414
MOBILE_SCREEN_HEIGHT = 896
MOBILE_SCREEN_PIXEL_RATIO = 2.0


def before_all(context):
    """Sets up the web application as test object and initializes chromedriver."""
    # Initialize the system in the same way as main.py
    app, _, launcher, roboclaw, epos, _ = initialize_system()

    # Disable debounce time limit to prevent issues when testing manual motor commands
    launcher.DEBOUNCE_TIME_LIMIT = 0

    # Set up the motor and climate mocks to have a starting point without errors
    store_motor_variables(context, launcher, epos, roboclaw)
    setup_motor_mocks(context)
    setup_climate_mocks(launcher)

    setup_gui_under_test(context, app)

    # Remember if running tests for old or new gui, to select which url to load
    context.new_gui = True


def setup_gui_under_test(context, app):
    """Starts the application under test and sets up the web driver."""
    context.server = simple_server.WSGIServer(("", APP_PORT), WSGIRequestHandler)
    context.server.set_app(app)
    context.pa_app = threading.Thread(target=context.server.serve_forever)
    context.pa_app.start()

    # Check if command line argument "browser" is set, if not default to Chrome.
    # Example: behave -D browser=safari
    try:
        browser = context.config.userdata['browser'].lower()
        if browser == "safari":
            context.browser = webdriver.Safari()
            context.browser.maximize_window()
        elif browser == "chrome":
            context.browser = webdriver.Chrome(options=chrome_options)
        elif browser == "mobile":
            setup_mobile_browser(context, width=MOBILE_SCREEN_WIDTH, height=MOBILE_SCREEN_HEIGHT,
                                 pixel_ratio=MOBILE_SCREEN_PIXEL_RATIO)
        elif browser == "mobile_landscape":
            # Inverts the default width and height
            setup_mobile_browser(context, width=MOBILE_SCREEN_HEIGHT, height=MOBILE_SCREEN_WIDTH,
                                 pixel_ratio=MOBILE_SCREEN_PIXEL_RATIO)
        else:
            raise ValueError(f"{browser} is not supported. ")
    except KeyError:
        context.browser = webdriver.Chrome(options=chrome_options)

    # Error handling for not supported browser
    except ValueError:
        context.browser = Mock()
        raise

    context.browser.set_page_load_timeout(time_to_wait=200)


def setup_mobile_browser(context, width, height, pixel_ratio):
    """
    Sets up and starts a mobile chrome webdriver based on device width and height.
    Input device not working Jenkins, so deviceMetrics are set manually.
    """
    mobile_emulation = {
        "deviceMetrics": {"width": width, "height": height, "pixelRatio": pixel_ratio},
        "userAgent": "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) "
                     "AppleWebKit/537.36 (KHTML, like Gecko)"
                     "Chrome/59.0.3071.125 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    context.browser = webdriver.Chrome(options=chrome_options)


def after_all(context):
    """Closes the resources that were created at setup."""
    context.browser.quit()
    context.server.shutdown()
    context.pa_app.join()


def before_feature(context, feature): # noqa, pylint: disable=unused-argument
    """
    Makes features tagged with @manual automatically be skipped without the need to specify it
    explicitly.
    """
    if "manual" in feature.tags:
        feature.skip("Marked with @manual")
        return

    if "new_gui" in feature.tags:
        context.new_gui = True
    else:
        context.new_gui = False


def before_scenario(context, scenario):
    """
    Reload application start page between scenarios.
    Skip scenarios that are marked with manual.
    """

    if "manual" in scenario.tags:
        scenario.skip("Marked with @manual")
        return

    if "new_gui" in scenario.tags:
        context.new_gui = True

    # Reset stored ActionChains cursor actions to release pressed buttons between scenarios.
    # Needs to be done before reloading the page to prevent issues with un-interactable elements
    actions = ActionChains(context.browser)
    actions.reset_actions()

    # Select page to load base on new gui or old. Do that here to reduce execution time for
    # loading twice
    if context.new_gui:
        context.browser.get(url=APP_URL)
    else:
        context.browser.get(url=APP_URL_OLD)

    # Reset all mocks to create a known starting point
    setup_motor_mocks(context)
    setup_climate_mocks(context.launcher)

    # Reset ready to launch flag
    context.launcher.ready_to_launch = False


def store_motor_variables(context, launcher, epos, roboclaw):
    """
    Stores the variables related to motors, objects and interfaces, to be used later in mocking
    @param context: context where the variables will be stored
    @param launcher: launcher model containing the motor objects
    @param epos: interface to the EPOS motor controller
    @param roboclaw: interface to the Roboclaw motor controller
    """
    # Store the non mocked motors to allow resetting to non mocked version. Use copy and not
    # deepcopy to make the new copy keep the interface references. This allows restoring to a non
    # mocked motor model but then mock a low level interface.

    context.non_mocked_motors = copy.copy(launcher.motors)
    # Store the models to make them available for the test steps, e.g. for mocking
    context.launcher = launcher
    context.epos = epos
    context.roboclaw = roboclaw


def setup_motor_mocks(context):
    """
    Prepare mocked motors and mocked motor model method calls.
    This will create a test environment without initial errors.
    """
    # Mock the motors to prevent hardware errors. The mocked motors makes it possible to verify that
    # e.g. an API request results in appropriate motor requests.

    # Reset all mocked motors to provide a known starting point for each scenario
    # Restore the original non mocked launch motor
    for name, motor in context.launcher.motors.items():
        if name == "drone_position":
            context.launcher.motors[name] = context.non_mocked_motors[name]
        else:
            # Handle setup and reset of mocks, to use this method in both before_all and
            # before_scenario
            if not isinstance(motor, MagicMock):
                context.launcher.motors[name] = MagicMock(motor)
            else:
                context.launcher.motors[name].reset_mock(return_value=True, side_effect=True)

        # Mock the position request for the motor to prevent issues with background position update
        context.launcher.motors[name].get_actual_position = Mock(return_value=0)

    # Reset the low level EPOS mocks to return 1 to indicate no error
    mock_epos_interface(context.epos.epos, return_value=1)


def setup_climate_mocks(launcher):
    """
    Mocks the methods of ClimateModel that interacts with hardware. Provides dummy values for
    temperature and humidity.
    """
    launcher.climate_control.get_data = Mock(return_value=[40.0, 25.3])

    # Reset mocks and forcing to known starting point
    launcher.climate_control.set_fans_force(False)
    launcher.climate_control.activate_fans = Mock()


def mock_epos_interface(epos_cdll, return_value):
    """
    Mocks the specified EPOS dll methods.
    :param epos_cdll: CDLL object for the EPOS dll whose methods shall be mocked.
    :param return_value: Return value of the mocked methods.
    """
    for method_name in mocked_epos_dll_methods:
        setattr(epos_cdll, method_name, Mock(return_value=return_value))


def before_tag(context, tag):
    """Changes browser settings for specific tag"""
    if tag == 'api':
        context.browser = wire_webdriver.Chrome(options=chrome_options)


def after_tag(context, tag):
    """Reverts browser settings for specific tag"""
    if tag == 'api':
        context.browser = webdriver.Chrome(options=chrome_options)
