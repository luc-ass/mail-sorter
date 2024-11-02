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

Please see the .example configuration files for more examples.