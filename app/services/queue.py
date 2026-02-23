def send_to_queue(report_id: int, message: str):
    print(f"[QUEUE] Processing report {report_id}")
    print(f"[MESSAGE] {message}")
