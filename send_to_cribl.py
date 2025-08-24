#!/usr/bin/env python3

import json
import os
import requests

CRIBL_HEC_URL = "https://<your-cribl-cloud>.cribl.cloud:8088/services/collector/event"
HEC_TOKEN = os.environ.get("CRIBL_HEC_TOKEN")
BATCH_SIZE = 5000
INPUT_FILE = "asparser/results.json"

def send_batch(events, batch_num):
    headers = {
        'Authorization': f'Splunk {HEC_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = ''.join(events)
    response = requests.post(CRIBL_HEC_URL, data=payload, headers=headers)
    if response.status_code == 200:
        print(f"[Batch {batch_num}] ✅ Successfully sent {len(events)} events")
    else:
        print(f"[Batch {batch_num}] ❌ Error {response.status_code}: {response.text}")

def main():
    batch = []
    total_events = 0
    batch_num = 1
    buffer = ""

    with open(INPUT_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            buffer += line
            if line.endswith('}'):  # crude way to detect end of JSON object
                try:
                    raw_event = json.loads(buffer)
                    wrapped_event = json.dumps({
                        "event": raw_event,
                        "sourcetype": "maxmind:asn",
                        "index": "maxmind"
                    }) + '\n'
                    batch.append(wrapped_event)
                    total_events += 1
                except json.JSONDecodeError:
                    print("Skipping malformed JSON object")
                buffer = ""

                if len(batch) >= BATCH_SIZE:
                    send_batch(batch, batch_num)
                    batch = []
                    batch_num += 1

        # Final batch
        if batch:
            send_batch(batch, batch_num)

    print(f"\n✅ All done! Total events processed: {total_events}")

if __name__ == "__main__":
    main()