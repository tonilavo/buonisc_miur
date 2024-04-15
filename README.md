The project aims to provide citizens with the possibility of submitting applications for contributions online to a public body, giving the body's staff the tools to check the applications.
The project consists of 2 parts. In the application form (frontend) interested citizens must first fill out a small form with the essential data to check whether they meet the requirements for submitting the application.
Once verified by the office (backend), it sends the citizen a token via email and the link for submitting the application.
The citizen then fills out the application with received token and sends the notification of the submission deadline to the office.
The backend allows the office to monitor the applications received, check the data entered and send a positive response or report errors to the citizen. In case of errors, the office can make the application editable again, allowing the citizen to make corrections from the link in the first email.
The project was created in Django 3.2, with the use of Javascript for the backend part. There are asynchronous tasks managed through Celery, user authentication towards LDAP server for the office personal.
