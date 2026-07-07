# AWS Static Website Project (S3 + CloudFront)

A simple static website hosted on Amazon S3 and distributed globally via CloudFront (HTTPS), extended with a serverless contact form.

## Architecture

```
User Browser
     │
     ▼
CloudFront (CDN, HTTPS)
     │
     ▼
S3 Bucket (static website hosting)
```

## What this project covers

- S3 bucket creation and static website hosting configuration
- Bucket policies for public read access
- CloudFront distribution as a CDN in front of S3
- HTTPS via CloudFront's default certificate
- Cache invalidation when content changes

## Files

| File | Purpose |
|---|---|
| `index.html` | Homepage with contact form |
| `error.html` | Custom 404 page |
| `bucket-policy.json` | Sample S3 bucket policy for public read access (replace `YOUR-BUCKET-NAME`) |
| `project-2-contact-form/lambda_function.py` | Lambda handler for the contact form |

## Deploy steps (summary)

1. Create an S3 bucket (globally unique name)
2. Enable "Static website hosting" on the bucket (index: `index.html`, error: `error.html`)
3. Uncheck "Block all public access" and apply the bucket policy in `bucket-policy.json`
4. Upload `index.html` and `error.html` to the bucket
5. Create a CloudFront distribution pointing at the S3 **website endpoint** (not the bucket ARN)
6. Set "Redirect HTTP to HTTPS" and default root object to `index.html`
7. Test via the CloudFront domain name

## Updating content

After changing `index.html` or `error.html`:
```bash
aws s3 cp index.html s3://YOUR-BUCKET-NAME/
aws cloudfront create-invalidation --distribution-id YOUR-DISTRIBUTION-ID --paths "/*"
```

## Cleanup

```bash
aws s3 rm s3://YOUR-BUCKET-NAME/index.html
aws s3 rm s3://YOUR-BUCKET-NAME/error.html
aws s3 rb s3://YOUR-BUCKET-NAME
```
Then disable and delete the CloudFront distribution in the console.

---

## Project 2: Serverless Contact Form

Added a contact form to the site, backed by API Gateway → Lambda → DynamoDB + SES.

### Architecture
```
Browser (contact form)
       │
       ▼
API Gateway (HTTP API, POST /contact)
       │
       ▼
Lambda (contactFormHandler)
       │
       ├──▶ DynamoDB (ContactFormMessages table)
       └──▶ SES (email notification)
```

### What this covers
- API Gateway HTTP APIs with Lambda proxy integration
- Lambda writing to DynamoDB and sending email via SES
- IAM execution roles for Lambda
- CORS configuration for cross-origin browser requests

### Debugging story
First submission attempt failed with a CORS error in the browser console, alongside a 404 on the preflight `OPTIONS` request. Root cause: the API only had a `POST /contact` route configured with no CORS settings, so API Gateway had nothing to respond with for the browser's automatic preflight check — surfacing as a CORS block rather than a clear error.

Fixed by setting CORS directly on the API:
```bash
aws apigatewayv2 update-api --api-id YOUR-API-ID \
  --cors-configuration AllowOrigins="*",AllowMethods="POST,OPTIONS",AllowHeaders="content-type"
```
HTTP APIs handle `OPTIONS` preflight automatically once CORS is configured — no separate route needed.

### Setup summary
1. Verify sender/recipient email in SES (sandbox mode is fine for personal use)
2. Create a DynamoDB table `ContactFormMessages` with partition key `messageId` (String)
3. Create an IAM role for Lambda with DynamoDB + SES permissions
4. Create the Lambda function (`contactFormHandler`, Python 3.12) using `lambda_function.py`
5. Create an API Gateway HTTP API with a `POST /contact` route integrated to the Lambda
6. Enable CORS on the API (`AllowOrigins: *`, `AllowMethods: POST,OPTIONS`, `AllowHeaders: content-type`)
7. Wire the API endpoint into the contact form's fetch call in `index.html`

## Author

Rohan — built as part of a hands-on AWS learning track (S3, CloudFront, Lambda, API Gateway, DynamoDB, SES).
