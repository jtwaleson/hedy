"""Routines for interacting with AWS."""
import json
import logging
import os
import threading

import boto3

import config
import utils

logger = logging.getLogger(__name__)


def s3_querylog_transmitter_from_env() -> None:
    """Return an S3 transmitter, or return None."""
    have_aws_creds = os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")

    if not have_aws_creds:
        logger.warning("Unable to initialize S3 querylogger (missing AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY)")
        return None

    return make_s3_transmitter(config.config["s3-query-logs"])


def s3_parselog_transmitter_from_env() -> None:
    """Return an S3 transmitter, or return None."""
    have_aws_creds = os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")

    if not have_aws_creds:
        logger.warning("Unable to initialize S3 parse logger (missing AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY)")
        return None

    return make_s3_transmitter(config.config["s3-parse-logs"])


# The 'boto3.client' method is not thread safe: https://github.com/boto/boto3/issues/1592
#
# Put a lock around it to make sure that when both log queues try to get an S3 client at the
# same time, they don't trample on each other.
BOTO3_LOCK = threading.Lock()


def make_s3_transmitter(s3config):
    """Make a transmitter function (for use with a LogQueue) which will save records to S3."""

    def transmit_to_s3(timestamp, records):
        """Transmit logfiles to S3 with default config."""

        # No need to configure credentials, we've already confirmed they are in the environment.
        with BOTO3_LOCK:
            s3 = boto3.client("s3", region_name=s3config["region"])

        # Grouping in the key is important, we need this to zoom into an interesting
        # log period.
        key = (
            s3config.get("prefix", "")
            + utils.isoformat(timestamp).replace("T", "/")
            + s3config.get("postfix", "")
            + ".jsonl"
        )

        # Store as json-lines format
        body = "\n".join(json.dumps(r) for r in records)

        s3.put_object(
            Bucket=s3config["bucket"], Key=key, StorageClass="STANDARD_IA", Body=body  # Cheaper, applicable for logs
        )
        logger.debug(f'Wrote {len(records)} query logs to s3://{s3config["bucket"]}/{key}')

    return transmit_to_s3
