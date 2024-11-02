""" mail-sorter: a script keeping your mailbox tidy """

import time
import datetime
import yaml
from imap_tools import MailBox, AND

# Load YAML configurations for mail server and sorting rules
with open('mail_sorting_rules.yaml', 'r', encoding='utf-8') as config_file:
    sorting_config = yaml.safe_load(config_file)

with open('mail_config.yaml', 'r', encoding='utf-8') as credentials_file:
    mail_config = yaml.safe_load(credentials_file)

def parse_duration(duration_str):
    """Converts duration string (e.g., '14d') into a timedelta object."""
    if duration_str.endswith("d"):
        return datetime.timedelta(days=int(duration_str[:-1]))
    return datetime.timedelta(days=7)  # default 7 days

def folder_exists(mailbox, folder_name):
    """Check if a folder exists on the server."""
    return folder_name in [folder.name for folder in mailbox.folder.list()]

def move_emails(mailbox, rule, move_limit=10):
    """Move emails based on a single rule with optimized querying and verbose output."""
    # Calculate date cutoff based on min_mail_age and convert to date only
    min_mail_age = parse_duration(rule.get('min_mail_age', '7d'))
    date_cutoff = (datetime.datetime.now() - min_mail_age).date()  # Convert to date

    # Build combined search criteria with all conditions
    criteria = {
        "seen": (rule.get("read_status", "seen") == "seen"),
        "date_lt": date_cutoff,
    }
    if "sender_contains" in rule:
        criteria["from_"] = rule["sender_contains"]
    if "subject_contains" in rule:
        criteria["subject"] = rule["subject_contains"]

    print(f"\nApplying rule: Moving emails from '{rule.get('input_folder', 'INBOX')}' "
          f"to '{rule['output_folder']}' with criteria:")
    print(f"  - Read status: {'seen' if rule.get('read_status') == 'seen' else 'unseen'}")
    print(f"  - Date before: {date_cutoff}")
    if "sender_contains" in rule:
        print(f"  - Sender contains: {rule['sender_contains']}")
    if "subject_contains" in rule:
        print(f"  - Subject contains: {rule['subject_contains']}")

    # Fetch emails with combined criteria
    emails = mailbox.fetch(AND(**criteria))
    emails_sorted = sorted(emails, key=lambda msg: msg.date)  # Oldest to newest
    print(f"Found {len(emails_sorted)} matching emails")

    emails_moved = 0
    
    for msg in emails_sorted:
        if emails_moved >= move_limit:
            print(f"Reached move limit of {move_limit} emails for this rule.")
            break
        print(f"Moving email with UID {msg.uid} dated {msg.date} to '{rule['output_folder']}'")
        mailbox.move(msg.uid, rule['output_folder'])
        emails_moved += 1
        time.sleep(6)  # Control rate: 10 emails per minute

    print(f"Completed rule: Moved {emails_moved} emails to '{rule['output_folder']}'")
    return emails_moved

def main():
    """ Main function for sorting mail. """
    # Extract credentials and server info from configuration
    username = mail_config['username']
    password = mail_config['password']
    server = mail_config['server']

    # Connect to email server
    with MailBox(server).login(username, password) as mailbox:
        total_moved = 0
        # Iterate through rules and apply them
        for rule in sorting_config.get('rules', []):
            moved = move_emails(mailbox, rule)
            total_moved += moved
            print(f"Applied rule for output folder '{rule['output_folder']}': Moved {moved} emails")

if __name__ == "__main__":
    main()
