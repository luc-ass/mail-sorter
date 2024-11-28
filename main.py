""" mail-sorter: a script keeping your mailbox tidy """

import datetime
import logging
import argparse
import yaml
from imap_tools import MailBox, AND


def parse_args():
    '''Parse command line arguments'''
    parser = argparse.ArgumentParser(description="Control logging levels from the command line")
    parser.add_argument(
        '--log', '-l',
        default='WARNING',
        help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
        )
    return parser.parse_args()


def configure_logging(args):
    '''Configure logging with arguments'''
    log_level = getattr(logging, args.log.upper(), logging.WARNING)  # Set logging level based on --log argument
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s',
        filename='mail-sorter.log'
        )

# Load YAML configurations for mail servers and sorting rules
with open("mail_sorting_rules.yaml", "r", encoding="utf-8") as config_file:
    sorting_config = yaml.safe_load(config_file)


with open("mail_config.yaml", "r", encoding="utf-8") as credentials_file:
    mail_config = yaml.safe_load(credentials_file)


def parse_duration(duration_str):
    """Converts duration string (e.g., '14d') into a timedelta object."""
    logging.debug('Duration string: %s', duration_str)
    if duration_str.endswith("d"):
        return datetime.timedelta(days=int(duration_str[:-1]))
    if duration_str.endswith("w"):
        return datetime.timedelta(days=int(duration_str[:-1] * 7))
    if duration_str.endswith("m"):
        return datetime.timedelta(days=int(duration_str[:-1] * 30))
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

    logging.debug(
        "Moving emails from %s to %s with criteria:", 
        input_folder, rule['output_folder']
    )
    logging.debug(
        "> Read status: %s", 'seen' if rule.get('read_status') == 'seen' else 'unseen'
    )
    logging.debug("> Date before: %s", date_cutoff)
    if "sender_contains" in rule:
        logging.debug("> Sender contains: %s", rule['sender_contains'])
    if "subject_contains" in rule:
        logging.debug("> Subject contains: %s", rule['subject_contains'])

    # Fetch emails with combined criteria, limited to max_emails_per_rule
    try:
        emails = list(mailbox.fetch(AND(**criteria), limit=max_emails_per_rule))
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Error fetching emails: %s", e)
        return 0

    # Collect UIDs for batch move
    uids_to_move = [msg.uid for msg in emails]
    if uids_to_move:
        logging.debug(
            "Batch moving %s emails to %s",
            len(uids_to_move), rule['output_folder']
        )
        mailbox.move(
            uids_to_move, rule["output_folder"]
        )  # Move all emails in a single batch

    logging.info(
        "Moved %s emails from '%s' to '%s'",
        len(uids_to_move), input_folder, rule['output_folder']
    )
    return len(uids_to_move)


def main():
    '''Main function'''
    # Configure logging based on arguments
    args = parse_args()
    configure_logging(args)

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

        logging.info(
            "Connecting to %s (%s) with username %s...",
            server_name, server, username
        )


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

            logging.info(
                "Completed processing for %s. Total emails moved: %s", 
                server_name, total_moved
                )


if __name__ == "__main__":
    main()
