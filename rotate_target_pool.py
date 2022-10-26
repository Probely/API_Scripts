#!/usr/bin/env python
import csv
import logging
import sys
from time import sleep
from urllib.parse import urlparse, urljoin

import requests

token = ""
base_url = "https://api.probely.com"
pool_size = 25
target_list_url = urljoin(base_url, "targets/")
target_detail_url = urljoin(base_url, "targets/{target_id}/")
start_scan_url = urljoin(base_url, "targets/{target_id}/scan_now/")
scan_detail_url = urljoin(base_url, "targets/{target_id}/scans/{scan_id}/")
finding_list_url = urljoin(base_url, "targets/{target_id}/findings/")
session = requests.Session()
sleep_time = 5 * 60  # 5 minutes
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


def create_target(url):
    hostname = urlparse(url).hostname
    logging.info("[%s] Creating target", hostname)
    target_payload = {
        "site": {
            "url": url,
            "name": hostname,
        },
        "labels": [
            {"name": "Test"},
        ],
    }
    response = session.post(target_list_url, json=target_payload)
    response.raise_for_status()
    return response.json()


def delete_target(target):
    logging.info("[%s] Deleting targets", target["site"]["name"])
    response = session.delete(target_detail_url.format(target_id=target["id"]))
    response.raise_for_status()


def start_scan(target):
    logging.info("[%s] Starting scan", target["site"]["name"])
    response = session.post(start_scan_url.format(target_id=target["id"]))
    response.raise_for_status()
    return response.json()


def get_scan(target, scan):
    logging.info("[%s] Retrieving scan", target["site"]["name"])
    response = session.get(
        scan_detail_url.format(target_id=target["id"], scan_id=scan["id"])
    )
    response.raise_for_status()
    return response.json()


def get_scan_findings(target, scan):
    page = 1
    page_total = 1
    findings = []
    while page <= page_total:
        response = session.get(
            finding_list_url.format(target_id=target["id"]),
            params={"scan": scan["id"], "length": 10000, "page": 1},
        )
        response.raise_for_status()
        response = response.json()
        findings.extend(response["results"])
        page_total = response["page_total"]
        page += 1
    return findings


def create_and_start_scan(target_url, running_scans):
    global pool_size
    logging.info("Starting %s", target_url)
    try:
        target = create_target(target_url)
        scan = start_scan(target)
    except requests.HTTPError as exc:
        if (
            exc.response.json().get("non_field_errors", "")
            and "The target pool of your subscription has no available slots"
            in exc.response.json().get("non_field_errors", "")[0]
        ):
            logging.error(
                "Reached pool limit before filling queue! Reducing pool size."
            )
            pool_size -= 1
            if pool_size == 0:
                logging.error("Unable to create any more targets")
                sys.exit(1)
        else:
            logging.error(exc)
            if hasattr(exc, "response"):
                logging.error(exc.response.content)
    else:
        running_scans[target["id"]] = (target, scan)


def save_and_delete(target, scan, output_file):
    with open(output_file, "at", newline="") as csv_file:
        csv_writer = csv.writer(
            csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        findings = get_scan_findings(target, scan)
        for finding in findings:
            csv_writer.writerow(to_csv(finding))
    delete_target(target)


def to_csv(result):
    labels = result["labels"] if result.get("labels") else []
    labels_name = [label["name"] for label in labels]
    row = [
        result["id"],
        result["severity"],
        result["definition"]["name"],
        result["url"],
        result["last_found"],
        result["state"],
        result.get("assignee")["email"] if result.get("assignee") else " ",
        *labels_name,
    ]
    return row


def main(target_list, output_file, token):
    # Add token to all requests
    global pool_size
    session.headers.update({"Authorization": f"JWT {token}"})

    running_scans = {}
    while True:
        # Create targets and start scans up to pool_size
        while len(running_scans) < pool_size:
            try:
                target_url = target_list.pop()  # Remove from queue
            except IndexError:
                break
            else:
                create_and_start_scan(target_url, running_scans)
            logging.info("%s Running scans", len(running_scans))

        sleep(sleep_time)  # Wait before checking scans

        # Check running scans
        logging.info("Checking on %s running scans", len(running_scans))
        finished_scans = []
        for target, scan in running_scans.values():
            scan = get_scan(target, scan)
            logging.info("[%s] Scan status %s", target["site"]["name"], scan["status"])
            if scan["status"] == "queued":
                logging.info("[%s] Scan hasn't started yet", target["site"]["name"])
            elif scan["status"] in ("cancelled", "failed"):
                logging.error(
                    "[%s] Scan has unexpectedly stopped", target["site"]["name"]
                )
            elif scan["status"] == "completed":
                logging.info("[%s] Scan has finished", target["site"]["name"])
                save_and_delete(target, scan, output_file)
                finished_scans.append(target["id"])
                logging.info(
                    "[%s] Results stored and target deleted", target["site"]["name"]
                )
            else:
                logging.info("[%s] Scan still running", target["site"]["name"])

        # Remove from running scans
        for id_ in finished_scans:
            del running_scans[id_]

        if not target_list and not running_scans:
            sys.exit(0)


if __name__ == "__main__":
    target_list = [
        "https://example.org",
    ]
    output_file = "/tmp/out.csv"
    main(target_list, output_file, token)
