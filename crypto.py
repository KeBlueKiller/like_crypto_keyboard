import keyboard
import time
import hashlib

# 用户存储结构
users = {}

def record_typing_behavior():
    print("Enter your password (visible for demonstration, press Enter to finish): ")
    events = keyboard.record(until='enter')
    
    current_chars = []
    press_times = {}
    backspace_count = 0
    
    for event in events:
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'backspace':
                if current_chars:
                    current_chars.pop()
                    backspace_count += 1
            else:
                if event.name not in ['enter', 'shift']:
                    press_times[event.scan_code] = event.time
        elif event.event_type == keyboard.KEY_UP:
            if event.name == 'backspace' or event.name == 'enter' or event.name == 'shift':
                continue
            scan_code = event.scan_code
            if scan_code in press_times:
                press_time = press_times.pop(scan_code)
                current_chars.append((event.name, press_time, event.time))
    
    if not current_chars:
        return "", [], [], 0
    
    # 计算击键间隔（按下时间差）
    intervals = []
    for i in range(1, len(current_chars)):
        intervals.append(current_chars[i][1] - current_chars[i-1][1])
    
    # 计算按键时长（释放时间 - 按下时间）
    durations = [char[2] - char[1] for char in current_chars]
    
    # 生成密码字符串
    password = ''.join([char[0] for char in current_chars])
    
    return password, intervals, durations, backspace_count

def verify_behavior(current_intervals, current_durations, current_edits, stored_intervals, stored_durations, stored_edits):
    if len(current_intervals) != len(stored_intervals) or len(current_durations) != len(stored_durations):
        return False
    
    interval_ok = True
    if len(current_intervals) > 0:
        avg_error = sum(abs(c - s) for c, s in zip(current_intervals, stored_intervals)) / len(current_intervals)
        interval_ok = avg_error <= 0.2  # 击键间隔平均误差阈值
    
    duration_ok = True
    if len(current_durations) > 0:
        avg_error = sum(abs(c - s) for c, s in zip(current_durations, stored_durations)) / len(current_durations)
        duration_ok = avg_error <= 0.1  # 按键时长平均误差阈值
    
    edit_ok = abs(current_edits - stored_edits) <= 1  # 允许修正次数误差1次
    
    return interval_ok and duration_ok and edit_ok

def register():
    username = input("Enter username: ")
    if username in users:
        print("Username already exists!")
        return
    
    password, intervals, durations, edits = record_typing_behavior()
    if not password:
        print("Password cannot be empty!")
        return
    
    users[username] = {
        'password_hash': hashlib.sha256(password.encode()).hexdigest(),
        'intervals': intervals,
        'durations': durations,
        'edits': edits
    }
    print("Registration successful!")

def login():
    username = input("Enter username: ")
    if username not in users:
        print("User not found!")
        return False
    
    stored = users[username]
    password, intervals, durations, edits = record_typing_behavior()
    
    if hashlib.sha256(password.encode()).hexdigest() != stored['password_hash']:
        print("Password incorrect!")
        return False
    
    if verify_behavior(intervals, durations, edits, stored['intervals'], stored['durations'], stored['edits']):
        print("Behavior verification passed!")
        return True
    else:
        print("Behavior verification failed!")
        return False

if __name__ == "__main__":
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose option: ")
        if choice == '1':
            register()
        elif choice == '2':
            login()
        elif choice == '3':
            break
        else:
            print("Invalid choice!")