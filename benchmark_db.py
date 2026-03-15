import time
from statistics import mean
from sqlalchemy import text
from core.database import SessionLocal

TEST_COUNT = 200


def test_latency():
    db = SessionLocal()

    times = []

    print(f"\nRunning latency test with {TEST_COUNT} queries...\n")

    for i in range(TEST_COUNT):
        start = time.perf_counter()

        db.execute(text("SELECT 1"))

        end = time.perf_counter()

        times.append((end - start) * 1000)  # convert to ms

    db.close()

    print("Results (milliseconds)")
    print("---------------------")
    print(f"Min latency : {min(times):.2f} ms")
    print(f"Max latency : {max(times):.2f} ms")
    print(f"Avg latency : {mean(times):.2f} ms")


if __name__ == "__main__":
    test_latency()