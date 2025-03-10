import argparse
from scripts.terracron import Terracron
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser(description="Scheduler script")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Subcommands')

    # Create a subparser for the 'schedule' command
    scheduler_parser = subparsers.add_parser('schedule', help='Schedule command')
    scheduler_parser.add_argument('--scheduler', type=str, default='./schedule.yaml', help='Path to the schedule YAML file')
    args = parser.parse_args()

    # load .env content to environment variables
    load_dotenv()

    if args.command == 'schedule':
        scheduler = Terracron(scheduler=args.scheduler)
        scheduler.schedule()

if __name__ == "__main__":
    main()
