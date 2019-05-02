from behave import *
from notify import Handler
from hamcrest import assert_that, equal_to, is_in, is_, not_none

use_step_matcher("re")


@given("a valid payload was sent")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.handler = Handler({
        "message_type": "email",
        "to": "example@example.com",
        "template_id": "1234-abcd-6789-efff",
        "template_vars": {
            "example_var": "var",
            "name": "Guido"
        },
        "attachment": "eyJkYXRhIjogInRoaXMgaXMgYW4gZXhhbXBsZSBiYXNlNjQgZW5jb2RlZCBmaWxlIn0K",
        "attachment_name": "example.json"
    })


@then("it should set the message")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert context.handler.message is not None


@when("I call the handler")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.handler.handle()


@then("it should send the message")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.handler.data, not_none())


@step("it should return a valid response")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    returned_with_data = {"response": context.handler.data}
    returned_with_no_response = {
        "response": f'Success but no response from sender: {type(context.handler.sender).__name__}'}
    assert_that(context.handler.response, is_in([returned_with_data, returned_with_no_response]))


@given('a valid "(?P<message_type>.+)" was sent')
def step_impl(context, message_type):
    """
    :type context: behave.runner.Context
    :type message_type: str
    """
    context.handler = Handler({
        "message_type": message_type
    })


@then('it should use the correct "(?P<sender>.+)"')
def step_impl(context, sender):
    """
    :type context: behave.runner.Context
    :type sender: str
    """
    assert_that(context.handler.sender.__name__, equal_to(sender))


@given("an invalid message type was sent")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.handler = Handler({
        "message_type": "invalid"
    })


@then("it should log a ValueError Exception")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """


@step("it should raise the Exception")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: And it should raise the Exception')
