# EmailAgent - Autonomous Personal Finance Email Agent

FinBot is an intelligent email agent that automatically processes incoming emails containing bills, invoices, receipts, and financial statements. It extracts financial information, sets reminders, sends alerts, and responds with professional confirmations.

## Features

- **🤖 Autonomous Email Processing**: Monitors Gmail inbox and automatically processes financial emails
- **📄 Document Analysis**: Extracts text from PDF attachments (invoices, receipts, statements)
- **💰 Financial Data Extraction**: Automatically identifies amounts, due dates, and categorizes expenses
- **⏰ Smart Reminders**: Sets calendar reminders for upcoming due dates
- **📧 Professional Responses**: Generates and sends professional email confirmations
- **🔍 Intelligent Reasoning**: Shows step-by-step decision making process

## How It Works

1. **Email Monitoring**: Uses Gmail IMAP IDLE to monitor for new emails in real-time
2. **Content Extraction**: Processes email content and extracts text from PDF attachments
3. **AI Analysis**: Uses GPT-4.1-mini to analyze financial documents and determine appropriate actions
4. **Tool Execution**: Automatically executes tools like storing data, setting reminders, or sending alerts
5. **Response Generation**: Composes and sends professional email responses

## Project Structure

```
EmailAgent/
├── agent/
│   ├── EmailAgent.py          # Main agent logic
│   ├── context.py             # User context management
│   ├── prompt.py              # System instructions for the AI
│   ├── reasoning_display.py   # Reasoning visualization
│   └── tools/                 # Agent tools
│       ├── store.py           # Financial data storage
│       ├── reminder.py        # Calendar reminders
│       ├── urgent.py          # Urgent alerts
│       └── abort_response.py  # No-reply handling
├── utils/
│   ├── email.py               # Gmail integration
│   └── parse.py               # Document parsing
├── main.py                    # Main application loop
├── constants.py               # Configuration constants
└── logger.py                  # Logging setup
```

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd EmailAgent
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Gmail OAuth**

   - Follow Google's Gmail API setup guide
   - Download your `credentials.json` file
   - Run the OAuth setup:

   ```bash
   python setup_gmail_oauth.py
   ```

4. **Configure environment variables**
   Create a `.env` file:

   ```env
   EMAIL_USER=your-email@gmail.com
   OPENAI_API_KEY=your-openai-api-key
   ```

5. **Update constants**
   Edit `constants.py`:
   ```python
   MAILBOX = "INBOX"  # Gmail folder to monitor
   ONLY_ANSWER_TO_EMAIL = "your-email@gmail.com"  # Email to respond to
   ```

## Usage

### Running the Agent

Start the email monitoring agent:

```bash
python main.py
```

The agent will:

- Connect to your Gmail inbox
- Monitor for new emails in real-time
- Process emails from your specified email address
- Extract and analyze financial documents
- Send appropriate responses

### Testing the Agent

You can test the agent by running it directly:

```bash
python agent/EmailAgent.py
```

This will process a sample invoice and show the reasoning process.

### Example Email Processing

**Input Email:**

```
From: vendor@company.com
Subject: Monthly Invoice
Body: Please find attached your monthly invoice.
Attachment: invoice.pdf
```

**Agent Actions:**

1. Extracts text from invoice.pdf
2. Identifies amount: $1,250.00, due date: July 15, 2025
3. Stores financial record
4. Sets calendar reminder
5. Sends urgent alert (high amount)
6. Responds with confirmation email

**Response Email:**

```
Subject: Invoice Processed - Thank You
Body: Dear Sender,

Thank you for your invoice. I have successfully processed it and stored
the details in my financial records.

The following actions were taken:
- Invoice stored with amount: $1,250.00
- Due date reminder set for: 2025-07-15
- Urgent alert sent due to high amount

Best regards,
FinBot
```

## Configuration

### Email Filtering

The agent only processes emails from addresses specified in `ONLY_ANSWER_TO_EMAIL`. This prevents unauthorized access and ensures only trusted senders trigger processing.

### Agent Behavior

The agent respects email instructions like:

- "Don't reply to this email"
- "No reply needed"
- "Do not respond"

When these phrases are detected, the agent processes the content but doesn't send a response.

### Tool Configuration

Tools can be customized in the `agent/tools/` directory:

- **store.py**: Modify financial data storage logic
- **reminder.py**: Customize reminder scheduling
- **urgent.py**: Adjust urgency thresholds
- **abort_response.py**: Handle no-reply scenarios

## Logging and Debugging

### View Reasoning

See detailed agent reasoning:

```bash
python view_reasoning.py
```

### Debug Mode

Enable detailed logging by setting `show_reasoning=True` in `main.py`.

### Log Files

- Application logs: Console output
- Reasoning logs: `logs/reasoning_log_*.json`
- Extracted documents: `tmp/`
