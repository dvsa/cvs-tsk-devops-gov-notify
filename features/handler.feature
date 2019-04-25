# Created by martinkemp at 2019-04-24
Feature: Handler
  # Enter feature description here

  Scenario: valid handler call
    Given a valid payload was sent
    When I call the handler
    Then it should send the message
    And return a response
