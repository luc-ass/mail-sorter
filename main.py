""" mail-sorter: a script keeping your mailbox tidy """

import datetime
import yaml
from imap_tools import MailBox, AND

# Load YAML configurations for mail servers and sorting rules
with open("mail_sorting_rules.yaml", "r", encoding="utf-8") as config_file:
    sorting_config = yaml.safe_load(config_file)

with open("mail_config.yaml", "r", encoding="utf-8") as credentials_file:
    mail_config = yaml.safe_load(credentials_file)


def parse_duration(duration_str):
    """Converts duration string (e.g., '14d') into a timedelta object."""
    if duration_str.endswith("d"):
        return datetime.timedelta(days=int(duration_str[:-1]))
    return datetime.timedelta(days=7)  # default 7 days


def move_emails(mailbox, rule, max_emails_per_rule):
    """Move emails based on a single rule with batch moving and verbose output."""
    # Select the input folder
    input_folder = rule.get("input_folder", "INBOX")
    mailbox.folder.set(input_folder)

    # Calculate date cutoff based on min_mail_age and convert to date only
    min_mail_age = parse_duration(rule.get("min_mail_age", "7d"))
    date_cutoff = (datetime.datetime.now() - min_mail_age).date()  # Convert to date

    # Build combined search criteria with all conditions, forcing string conversion
    criteria = {
        "seen": (rule.get("read_status", "seen") == "seen"),
        "date_lt": date_cutoff,
    }
    if "sender_contains" in rule:
        criteria["from_"] = str(rule["sender_contains"])
    if "subject_contains" in rule:
        criteria["subject"] = str(rule["subject_contains"])

    print(
        f"\nApplying rule: Moving emails from '{input_folder}' "
        f"to '{rule['output_folder']}' with criteria:"
    )
    print(
        f"  - Read status: {'seen' if rule.get('read_status') == 'seen' else 'unseen'}"
    )
    print(f"  - Date before: {date_cutoff}")
    if "sender_contains" in rule:
        print(f"  - Sender contains: {rule['sender_contains']}")
    if "subject_contains" in rule:
        print(f"  - Subject contains: {rule['subject_contains']}")

    # Fetch emails with combined criteria, limited to max_emails_per_rule
    try:
        emails = list(mailbox.fetch(AND(**criteria), limit=max_emails_per_rule))
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return 0

    emails_sorted = sorted(emails, key=lambda msg: msg.date)[
        :max_emails_per_rule
    ]  # Oldest to newest
    print(
        f"Found {len(emails_sorted)} matching emails in '{input_folder}', limited to {max_emails_per_rule}"
    )

    # Collect UIDs for batch move
    uids_to_move = [msg.uid for msg in emails_sorted]
    if uids_to_move:
        print(f"Batch moving {len(uids_to_move)} emails to '{rule['output_folder']}'")
        mailbox.move(
            uids_to_move, rule["output_folder"]
        )  # Move all emails in a single batch

    print(
        f"Completed rule: Moved {len(uids_to_move)} emails from '{input_folder}' to '{rule['output_folder']}'"
    )
    return len(uids_to_move)


def main():
    # Extract global defaults from the configuration
    global_max_emails_per_rule = sorting_config.get("defaults", {}).get(
        "max_emails_per_rule", 10
    )

    # Iterate over each server configuration
    for server_config in mail_config["servers"]:
        server_name = server_config["name"]
        server = server_config["server"]
        username = server_config["username"]
        password = server_config["password"]

        print(f"\nConnecting to {server_name} ({server}) with username {username}...")

        # Connect to the email server
        with MailBox(server).login(username, password) as mailbox:
            total_moved = 0

            # Apply each rule that includes this server
            for rule in sorting_config["rules"]:
                if server_name in rule["servers"]:
                    # Use rule-specific settings if present; otherwise, use global defaults
                    max_emails_per_rule = rule.get(
                        "max_emails_per_rule", global_max_emails_per_rule
                    )

                    moved = move_emails(mailbox, rule, max_emails_per_rule)
                    total_moved += moved

            print(
                f"\nCompleted processing for {server_name}. Total emails moved: {total_moved}"
            )


if __name__ == "__main__":
    main()
