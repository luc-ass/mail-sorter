# mail-sorter
**mail-sorter** is a script for keeping your mailbox tidy. You provide it whit a `mail_config.yaml` and a `mail_sorting_rules.yaml` and it will sort your mail based on the following criteria:

| criterion (defaults)  | example | default | optional |
| :-------------------- | :------ | :------ | :------- |
| `max_emails_per_rule` | `50`    | `10`    | yes      |

| criterion (rules)  | example                | default | optional |
| :----------------- | :--------------------- | :------ | :------- |
| `input_folder`     | `Office/Important`     | `INBOX` | yes      |
| `output_folder`    | `Office/Important/Old` |         | no       |
| `sender_contains`  | `@example.com`         |         | yes      |
| `subject_contains` | `Meeting Notes`        |         | yes      |
| `min_mail_age`     | `14d`                  | `7d`    | yes      |
| `read_status`      | `unseen`               | `seen`  | yes      |

## Configuration files
### mail_config
Your `mail_config.yaml` contains the information about your email servers and login credentials. Be sure to keep these secure. I've kept them in a seperate file, so you can share and backup your rules more easily, as the rules file can become quite big. Your configuration could look like this:

```yaml
servers:
  - name: "Google Mail"
    server: "imap.gmail.com"
    username: "your_google_email@example.com"
    password: "your_google_password"
  
  - name: "Second Server"
    server: "imap.secondserver.com"
    username: "your_second_email@example.com"
    password: "your_second_password"
```

### mail_sorting_rules
Your `mail_sorting_rules.yaml` contains the actual sorting rules. These can be configured to run on only one or multiple of your accounts:

```yaml
defaults:
  max_emails_per_rule: 10 # Maximum number of emails to move per rule

rules:
  - servers:
      - "Google Mail"
      - "Second Server"
    input_folder: "INBOX"
    output_folder: "Belege/Paypal"
    sender_contains: "@paypal.com"
    subject_contains: "Zahlung"
    min_mail_age: "14d"
    read_status: "seen"
  
  - servers:
      - "Second Server"
    input_folder: "INBOX"
    output_folder: "Promotions"
    sender_contains: "@newsletter.com"
    min_mail_age: "30d"
    read_status: "unseen"
```
Be careful to use multiple servers in one rule, as these rules and underlying folders need to be identical. Differing folder structure can make this script fail.

### Install & run
```sh
# create virtual environment if not exits
python3 -m venv .venv
# activate envirnoment
source .venv/bin/activate
# install requirements
pip install -r requirements.txt
# run mail-sorter
python3 main.py
```