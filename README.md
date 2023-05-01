# DayXDay

DayXDay is an app that helps you organize daily tasks and notes by automatically classifying them into various categories. It generates a personalized daily briefing based on the tasks and sends an email with the report.

## Features

- Automatically classifies notes into categories like Personal, Work, Health, Finance, and more
- Generates a daily briefing based on the tasks
- Sends an email with the generated report using SendGrid (optional)
- Allows marking tasks as complete
- Stores encrypted notes securely
- Displays all notes and past reports

##Requirements

- Python 3.x
- OpenAI API key
- SendGrid API key (optional)

Before installing and running the code, make sure you have Python 3.x installed on your system. You can download the latest version of Python from the official website: https://www.python.org/downloads/

You also need an OpenAI API key to use the app. You can get an API key by signing up for OpenAI at https://openai.com/signup/. Once you have an API key, you'll need to add it to the config.py file in the project directory.

If you want to enable email reports, you'll also need a SendGrid API key. You can sign up for SendGrid at https://sendgrid.com/free/. Once you have an API key, you'll need to add it to the config.py file in the project directory.

Note that the SendGrid API key is optional. You can still use the app without it, but you won't be able to send email reports.

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/DayXDay.git
   ```

2. Navigate to the project directory:

   ```
   cd DayXDay
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Edit the `config.py` file in the project directory with the following content:

   ```
   OPENAI_API_KEY = "<your_openai_api_key>"
   DEFAULT_PASSWORD = "<your_default_password>"
   SECRET_KEY = "<your_flask_secret_key>"
   SALT = "<your_salt>"
   SENDGRID_API_KEY = "<your_sendgrid_api_key>"  # Optional for sending email reports
   ```

   Replace `<your_openai_api_key>` with your OpenAI API key, `<your_default_password>` with a secure password, `<your_flask_secret_key>` with a Flask secret key, `<your_salt>` with a salt for encryption, and `<your_sendgrid_api_key>` with your SendGrid API key (if you want to enable email reports).

## Usage

This app is optimized for deploying on [Replit](https://replit.com/); however, you can also modify it for local deployment.

1. Run the app:

   ```
   python app.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:8080/` (for local deployment) or the appropriate URL when deployed on Replit.

3. Log in with the default password you set in the `config.py` file.

4. Start adding notes. The app will automatically classify them into categories.

5. View your notes and generated reports on the home page.

6. Generate a new report on demand by clicking the "Generate Report" button.

7. Mark tasks as complete to remove them from the list.

8. Optionally, you can set up cron jobs to automatically send daily email reports using the SendGrid API key provided in the `config.py` file.

## Contributing

If you'd like to contribute to the project, please submit a pull request with your changes.

## License

This project is licensed under the MIT License.
