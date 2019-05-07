import boto3
import responses
from behave import use_step_matcher, given, then, when

from boto3_type_annotations.s3 import ServiceResource
from hamcrest import assert_that, equal_to, is_in, not_none, calling, raises
from moto import mock_s3, mock_xray_client, XRaySegment

from notify import Handler

use_step_matcher("re")


@mock_xray_client
@mock_s3
@given("a valid payload was sent")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    sess = boto3.Session('test', 'test', 'test', 'eu-west-1')
    with XRaySegment():
        s3: ServiceResource = sess.resource('s3')
        s3.create_bucket(Bucket='cvs-devops-notifications')
    with XRaySegment():
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
    assert_that(context.handler.message, not_none())


@when("I call the handler")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    with responses.RequestsMock() as resps:
        resps.add(resps.POST, 'https://api.notifications.service.gov.uk/v2/notifications/email', body='{}', status=200,
                  content_type='application/json')
        context.response = context.handler.handle()


@then("it should send the message")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(context.handler.data, not_none())
    assert_that(context.response, not_none())


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
    context.handler.set_sender()
    assert_that(type(context.handler.sender).__name__, equal_to(sender))


@given("an invalid message type was sent")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.handler = Handler({
        "message_type": "invalid"
    })


@then("it should raise a ValueError Exception")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert_that(calling(context.handler.handle), raises(KeyError))
