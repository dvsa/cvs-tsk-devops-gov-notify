# Created by Martin Kemp at 2019-04-24
Feature: Handler
  The lambda handler

  Scenario: A valid handler call
    Given a valid payload was sent
    Then it should set the message
    When I call the handler
    Then it should send the message
    And it should return a valid response

  Scenario Outline: Valid message types

    Given a valid "<message_type>" was sent
    Then it should use the correct "<sender>"
    Examples: Event
      | message_type | sender    |
      | email        | GovNotify |
      | sms          | GovNotify |
      | teams        | Teams     |

  Scenario: invalid message type sent
    Given an invalid message type was sent
    Then it should log a ValueError Exception
    And it should raise the Exception
