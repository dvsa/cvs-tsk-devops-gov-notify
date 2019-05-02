# CVS DevOps Notification Lambda

This lambda is a generic application to enable the CVS DevOps team to be notified through email or sms.

You will require a GovNotify API Key to be able to use this lambda.

Any GovNotify templates to be used with will require a variable `s3_link` to allow attachments to be linked. 


## Config
Should be the following, you can exclude certain sections if you do not wish to use it.
```ini
[S3]
bucket_name = example-bucket
[GovNotify]
api_key = asjdahkdhawf-askljdalskjd-lkaskdjals
reply_to_id = safajkskasjhsfa-asldjaslkdjas-kljaslkdja
[Teams]
webhook_url = https://outlook.office.com/webhook/...
```

## Payloads

The values `template_vars` `attachment` `attachment_name` are optional. 

### Example payloads
[See the examples folder](./examples)

## Quick Start
Run the following:
```bash
pipenv install --dev
export TEAMS_URL='https://outlook.office.com/webhook/...'
pipenv run notify --event examples/teams.json
```

## Tests

NOTE: Tests are incomplete and will fail.

Simply run the following:
```bash
behave
```