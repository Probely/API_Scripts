#!/usr/bin/env python

"""
Script to list the number of vulnerabilities for each target of the account
"""


import csv
import requests
from urllib.parse import urljoin

def fetch_all_targets(api_base_url, headers):
    resp = requests.get(urljoin(api_base_url, "targets/?length=10000"), headers=headers)
    resp.raise_for_status()
    return resp.json().get("results", [])

def fetch_target_findings(api_base_url, target_id, headers):
    endpoint = urljoin(api_base_url, f"targets/{target_id}/findings/?length=10000")
    resp = requests.get(endpoint, headers=headers)
    resp.raise_for_status()
    return resp.json().get("results", [])

def count_severity(findings):
    high = sum(1 for f in findings if f.get("severity") == 30 or f.get("severity") == "HIGH")
    med  = sum(1 for f in findings if f.get("severity") == 20 or f.get("severity") == "MEDIUM")
    low  = sum(1 for f in findings if f.get("severity") == 10 or f.get("severity") == "LOW")
    return high, med, low

def main():
    token = input("API Token: ")
    instance = input("Instance (eu, us, au): ")
    csv_path = input("CSV file path (default: ./targets_findings.csv): ") or "./targets_findings.csv"
    headers = {"Authorization": f"JWT {token}", "Content-Type": "application/json"}
    api_base = f"https://api.{instance}.probely.com"

    print("Fetching targets...")
    try:
        targets = fetch_all_targets(api_base, headers)
    except requests.HTTPError as e:
        print("Failed to fetch targets:", e)
        return

    if not targets:
        print("No targets found.")
        return

    print(f"Found {len(targets)} target(s). Fetching findings per target...")

    with open(csv_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Target URL", "Target Name", "High Vulns", "Medium Vulns", "Low Vulns"])

        for t in targets:
            target_id = t.get("id", "")
            target_url = t.get("site", {}).get("url", "Unknown")
            target_name = t.get("name", "")

            try:
                findings = fetch_target_findings(api_base, target_id, headers)
            except requests.HTTPError:
                print(f"Warning: Could not fetch findings for target {target_url} (ID: {target_id})")
                writer.writerow([target_url, target_name, "N/A", "N/A", "N/A"])
                continue

            high, med, low = count_severity(findings)
            writer.writerow([target_url, target_name, high, med, low])

    print(f"Done! Results saved to {csv_path}")

if __name__ == "__main__":
    main()