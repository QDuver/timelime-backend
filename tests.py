import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email

sg = SendGridAPIClient('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')

html_content = "<p>Hello World!</p>"

message = Mail(
    to_emails="quentin.duverge@gmail.com",
    from_email=Email('quentin.duverge@gmail.com', "Your name"),
    subject="Hello world",
    html_content=html_content
    )
response = sg.send(message)
