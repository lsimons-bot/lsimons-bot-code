import argparse
import asyncio
import logging
import sys

from lsimons_bot.blog.publish import check_and_publish


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish blog posts about recent GitHub activity")
    parser.add_argument("--dry-run", action="store_true", help="Check but don't publish")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        result = asyncio.run(check_and_publish(dry_run=args.dry_run))
    except Exception as e:
        logging.error("Failed: %s", e)
        return 1

    print(result.reason)

    if result.post:
        print(f"URL: {result.post.link}")

    return 0 if not result.should_publish or result.post else 1


if __name__ == "__main__":
    sys.exit(main())
