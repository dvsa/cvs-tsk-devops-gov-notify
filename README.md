# CVS DevOps Notification Lambda

This lambda is a generic application to enable the CVS DevOps team to be notified through email or sms.

You will require a GovNotify API Key to be able to use this lambda.

Any GovNotify templates to be used with will require a variable `s3_link` to allow attachments to be linked. 


## Payloads

The values `template_vars` `attachment` `attachment_name` are optional. 

### Example payloads
#### Email
```json
{
  "message_type": "email",
  "to": "example@example.com",
  "template_id": "1234-abcd-6789-efff",
  "template_vars": {
    "example_var": "var",
    "name": "Guido"
  },
  "attachment": "eyJkYXRhIjogInRoaXMgaXMgYW4gZXhhbXBsZSBiYXNlNjQgZW5jb2RlZCBmaWxlIn0K",
  "attachment_name": "example.json"
}
```
#### SMS
```json
{
  "message_type": "sms",
  "to": "+447700900999",
  "template_id": "1234-abcd-6789-e555",
  "template_vars": {
    "example_var": "var",
    "name": "Guido"
  },
  "attachment": "eyJkYXRhIjogInRoaXMgaXMgYW4gZXhhbXBsZSBiYXNlNjQgZW5jb2RlZCBmaWxlIn0K",
  "attachment_name": "example.json"
}
```

## Quick Start
Run the following:
```bash
pipenv install --dev
pipenv run notify --event example_event.json
```

## Tests

NOTE: Tests are incomplete and will fail.

Simply run the following:
```bash
behave
```