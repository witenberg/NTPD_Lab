import csv
import os
import random
import sys
import time
from datetime import datetime, timedelta

INPUT_DIR = "data/input_stream"

CATEGORIES = ["books", "electronics", "food", "sports"]
STATUSES = ["paid", "paid", "paid", "cancelled", "pending"]


def generate_file(file_index: int) -> str:
    os.makedirs(INPUT_DIR, exist_ok=True)
    path = os.path.join(INPUT_DIR, f"events_{file_index:04d}.csv")

    now = datetime.now()
    rows = []
    for _ in range(random.randint(5, 10)):
        # czesc zdarzen jest celowo opozniona, zeby przetestowac watermarking
        if random.random() < 0.2:
            event_time = now - timedelta(minutes=random.randint(15, 40))
        else:
            event_time = now - timedelta(seconds=random.randint(0, 60))

        rows.append([
            event_time.strftime("%Y-%m-%d %H:%M:%S"),
            f"u{random.randint(1, 50):03d}",
            random.choice(CATEGORIES),
            round(random.uniform(5, 500), 2),
            random.choice(STATUSES),
        ])

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["event_time", "user_id", "category", "amount", "status"])
        writer.writerows(rows)

    return path


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

    # numeracja kontynuowana od istniejacych plikow
    os.makedirs(INPUT_DIR, exist_ok=True)
    start = len(os.listdir(INPUT_DIR))

    for i in range(start, start + count):
        path = generate_file(i)
        print(f"generated: {path}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
