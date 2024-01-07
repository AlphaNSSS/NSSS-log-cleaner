from datetime import datetime
from os.path import exists
from inspect import signature
from enum import Enum
import json

raw_time_start = 11
raw_line_start = 27
time_end = 9
line_start = 17

def clean_ports_from_IP(text: str):
    IP_pos = text.find("[", time_end)
    port_pos = text.find(":", IP_pos)
    port_end_pos = text.find("]", port_pos)
    if port_pos != -1:
        port = text[port_pos:port_end_pos]
        if port[1:].isnumeric() and port[0] == ":":
            text = text.replace(port, "")
    return text

def check_for_IP_at_index(text: str, index: int):
    IP_index = text.find("/", time_end)
    if IP_index != -1:
        IP_str = text[IP_index:IP_index + 3]
        if IP_str[1:].isnumeric() and IP_str[0] == "/":
            return IP_index == index
    return False

def clean_login(text: str, raw_text: str):
    coords = []

    username_index = time_end
    username_end_index = text.find(" ", username_index)
    username_IP_end_index = text.find("]", username_index) + 1

    coord_start_index = text.find("(", time_end) + 1
    for i in range(3):
        coord_end = text.find(".", coord_start_index)
        coords.append(text[coord_start_index:coord_end])
        coord_start_index = text.find(" ", coord_end) + 1

    username_IP = text[username_index:username_IP_end_index]
    username_IP = username_IP.replace("/", "")

    username = text[username_index:username_end_index]
    year = int(raw_text[:4])
    month = int(raw_text[5:7])
    day = int(raw_text[8:10])
    hour = int(text[:2])
    minute = int(text[3:5])
    second = int(text[6:8])
    players_login_times[username] = datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)

    clean_text = text[:time_end] + "  LOGIN " + username_IP + " at X:{} Y:{} Z:{}\n".format(coords[0], coords[1], coords[2])
    return clean_text

def clean_logout(text: str, raw_text: str):
    username_index = time_end
    username_end_index = text.find(" ", username_index)
    username = text[username_index:username_end_index]

    year = int(raw_text[:4])
    month = int(raw_text[5:7])
    day = int(raw_text[8:10])
    hour = int(text[:2])
    minute = int(text[3:5])
    second = int(text[6:8])
    current_time = datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
    time_spent = current_time - players_login_times[username]
    full_seconds_spent = int(time_spent.total_seconds())
    hours_spent = full_seconds_spent // 3600
    minutes_spent = (full_seconds_spent % 3600) // 60
    if full_seconds_spent < 120:
        time_spent = str(full_seconds_spent) + "s"
    elif full_seconds_spent < 6000:
        time_spent = str(minutes_spent) + "min"
    else:
        time_spent = "{}h {}min".format(hours_spent, minutes_spent)

    players_login_times.pop(username)

    clean_text = text[:time_end] + " LOGOUT " + username + " after {}\n".format(time_spent)
    return clean_text

def clean_chat(text: str):
    text = text[:time_end] + "        " + text[time_end:]

    opening_bracket_pos = text.find("<", line_start)
    closing_bracket_pos = text.find(">", line_start)
    # get longest name and center conversation around that
    longest_name = 0
    for player_name in players_login_times:
        length = len(player_name)
        if longest_name < length:
            longest_name = length

    opening_bracket_garbage = text[opening_bracket_pos:opening_bracket_pos + 4]
    closing_bracket_garbage = text[closing_bracket_pos - 3:closing_bracket_pos + 2]

    username = text[opening_bracket_pos:closing_bracket_pos + 2]
    username = username.replace(opening_bracket_garbage, "")
    username = username.replace(closing_bracket_garbage, "")

    global last_chatter
    invisible = False
    if last_chatter == username:
        invisible = True
    else:
        last_chatter = username

    missing_length = longest_name - len(username)

    compensation = ""
    for i in range(missing_length):
        compensation += " "

    if not invisible:
        text = text.replace(opening_bracket_garbage, "- " + compensation)
        text = text.replace(closing_bracket_garbage, ": ")
    else:
        text = text.replace(opening_bracket_garbage, "  " + compensation)
        text = text.replace(closing_bracket_garbage, "- ")
        
    if invisible:
        inv_compensation = ""
        for i in range(len(username)):
            inv_compensation += " "
        text = text.replace(username, inv_compensation)

    global keep_last_chatter
    keep_last_chatter = True

    return text

def clean_trycommand(text: str):
    username_index = time_end
    username_end_index = text.find(" ", username_index)
    username = text[username_index:username_end_index]

    command_index = text.find(":", username_end_index) + 2
    end_of_the_line = len(text) - 1 # end of the line, pal

    clean_text = text[:time_end] + "!!! CMD " + username + " tried /" + text[command_index:end_of_the_line] + " (failed)\n"
    return clean_text

def clean_command(text: str):
    username_index = time_end
    username_end_index = text.find(" ", username_index)
    username = text[username_index:username_end_index]

    command_index = text.find(":", username_end_index) + 2
    end_of_the_line = len(text) - 1

    clean_text = text[:time_end] + "!!! CMD " + username + " issued /" + text[command_index:end_of_the_line] + " (success)\n"
    return clean_text


raw_log = input("Enter log file path: ")
if not raw_log.endswith(".log"):
    print("ERROR: This isn't even a log file! Enter a valid one.")
    print("Exiting program...")
    exit()

print("Opening files...")

filter = {}
with open("filters.json", "r") as file:
    filter = file.read() # Read file as plaintext
    filter = json.loads(filter) # Turn plaintext into dictionary

raw_log = open(raw_log, "r")
cleaned_log = open("cleaned.log", "w")

raw_lines = raw_log.readlines()
cleaned_lines = [
    "Log cleaned at {}\n".format(datetime.now())
]

print("Begin filtration")

# values can be accessed at xyz.value["item_to_access"]
class FormatType(Enum):
    Chat = {
        "filters": ["<", ">"]
    }
    Login = {
        "filters": ["logged in with entity id"]
    }
    Logout = {
        "filters": ["lost connection"]
    }
    TryCommand = {
        "filters": ["tried command"]
    }
    Command = {
        "filters": ["issued server command"]
    }

filter_start_time = datetime.now()
players_login_times = {}
last_chatter = ""
day_timestamp = ""
keep_last_chatter = False
for raw_line in raw_lines:
    # check if the line should be filtered out
    found_illegal = False
    if not ("<" in raw_line and ">" in raw_line): # if override condition is not met, run the filter
        for item in filter:
            low_line = raw_line.lower()
            if item.lower() in low_line or check_for_IP_at_index(low_line, raw_line_start):
                found_illegal = True
                break

    # what should be done if it's not filtered out
    if not found_illegal:
        keep_last_chatter = False

        if len(players_login_times) == 0:
            cleaned_lines.append("\n")

        if day_timestamp != raw_line[:raw_time_start - 1]:
            day_timestamp = raw_line[:raw_time_start - 1]
            if len(players_login_times) == 0:
                cleaned_lines.append("========================================== {} ==========================================\n\n".format(day_timestamp))
            else:
                cleaned_lines.append("{} ==========\n".format(day_timestamp))

        clean_line = raw_line[raw_time_start:]
        clean_line = clean_line.replace("[INFO] ", "")
        clean_line = clean_ports_from_IP(clean_line)

        # check for a set of different conditions
        # line formatting depends on what condition is met first
        for format_type in FormatType:
            correct_type = False
            for val in format_type.value["filters"]:
                correct_type = val in clean_line
            if correct_type:
                formatting_function = f"clean_{format_type.name.lower()}"
                formatting_function = globals()[formatting_function] # converts string to function
                if len(signature(formatting_function).parameters) == 1:
                    clean_line = formatting_function(clean_line)
                else:
                    clean_line = formatting_function(clean_line, raw_line)
                break

        cleaned_lines.append(clean_line)

        if not keep_last_chatter:
            last_chatter = ""

seconds_taken_to_filter = (datetime.now() - filter_start_time).seconds
microseconds_taken_to_filter = (datetime.now() - filter_start_time).microseconds
print("Filtered {} lines in {}.{} seconds.".format(len(raw_lines), seconds_taken_to_filter, microseconds_taken_to_filter))
print("Writing new file")

cleaned_log.writelines(cleaned_lines)
cleaned_log.close()

print("All done!")
