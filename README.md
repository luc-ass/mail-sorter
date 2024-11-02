# mail-sorter
**mail-sorter** is a script for keeping your mailbox tidy. You provide it whit a `mail_config.yaml` and a `mail_sorting_rules.yaml` and it will sort your mail based on the following criteria:

| criterion          | example                | default | optional |
| :----------------- | :--------------------- | :------ | :------- |
| `input_folder`     | `Office/Important`     | `INBOX` | yes      |
| `output_folder`    | `Office/Important/Old` |         | no       |
| `sender_contains`  | `@example.com`         |         | yes      |
| `subject_contains` | `Meeting Notes`        |         | yes      |
| `min_mail_age`     | `14d`                  | `7d`    | yes      |
| `read_status`      | `unseen`               | `seen`  | yes      |

## Configuration files
### mail_config
Your `mail_config.yaml` contains the information about your email servers and login credentials. Be sure to keep these secure. Your configuration could look like this:

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
You should be careful to use multiple servers, as these rules are identical. Differing folder structure can make this script fail.