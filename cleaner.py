import datetime

raw_time_start = 11
raw_line_start = 27
line_start = 11

def clean_ports_from_IP(text: str):
    IP_pos = text.find("[", line_start)
    port_pos = text.find(":", IP_pos)
    port_end_pos = text.find("]", port_pos)
    if port_pos != -1:
        port = text[port_pos:port_end_pos]
        if port[1:].isnumeric() and port[0] == ":":
            text = text.replace(port, "")
    return text

def check_for_IP_at_index(text: str, index: int):
    IP_index = text.find("/", line_start)
    if IP_index != -1:
        IP_str = text[IP_index:IP_index+3]
        if IP_str[1:].isnumeric() and IP_str[0] == "/":
            return IP_index == index
    return False

def clean_login(text: str, raw_text: str):
    coords = []

    username_index = line_start
    username_end_index = text.find(" ", username_index)
    username_IP_end_index = text.find("]", username_index) + 1

    coord_start_index = text.find("(", line_start) + 1
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
    players_logon_times[username] = datetime.datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)

    clean_text = text[:line_start] + "LOGIN  -> " + username_IP + " at ({},{},{})\n".format(coords[0], coords[1], coords[2])
    return clean_text

def clean_logout(text: str, raw_text: str):
    username_index = line_start
    username_end_index = text.find(" ", username_index)
    username = text[username_index:username_end_index]

    year = int(raw_text[:4])
    month = int(raw_text[5:7])
    day = int(raw_text[8:10])
    hour = int(text[:2])
    minute = int(text[3:5])
    second = int(text[6:8])
    current_time = datetime.datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
    time_spent = current_time - players_logon_times[username]
    time_spent = str(time_spent)
    if time_spent[0] == "0":
        time_spent = time_spent[2:]

    players_logon_times.pop(username)

    clean_text = text[:line_start] + "LOGOUT <- " + username + " after {} minutes\n".format(time_spent)
    return clean_text


filter = [
    "Unknown console command.",
    "Starting NSSS server",
    "Loading properties",
    "Starting Minecraft server on",
    "WARNING",
    "Preparing level",
    "Preparing start region for",
    "For help, type",
    "Stopping server",
    "Saving chunks",
    "Forcing save",
    "Save complete",
    "Stopping the server",
    "Uwaga",
    "Maxcraft",
    "Disconnecting"
]

print("Opening files...")

raw_log = open('server.log', 'r')
cleaned_log = open('cleaned.log', 'w')

raw_lines = raw_log.readlines()
cleaned_lines = []

print("Begin filtration")

players_logon_times = {}
day_timestamp = ""
iteration = 0
for line in raw_lines:
    # check if the line should be filtered out
    found_illegal = False
    for item in filter:
        low_line = line.lower()
        if low_line.__contains__(item.lower()) or check_for_IP_at_index(low_line, raw_line_start):
            found_illegal = True

    # what should be done if it's not filtered out
    if not found_illegal:
        if day_timestamp != line[:line_start - 1]:
            day_timestamp = line[:line_start - 1]
            cleaned_lines.append("========================================== {} ==========================================\n".format(day_timestamp))

        clean_line = line[raw_time_start:]
        clean_line = clean_line.replace("[INFO]", "|")
        clean_line = clean_ports_from_IP(clean_line)

        if clean_line.__contains__("logged in with entity id"):
            clean_line = clean_login(clean_line, line)
        if clean_line.__contains__("lost connection"):
            clean_line = clean_logout(clean_line, line)

        cleaned_lines.append(clean_line)

        iteration += 1

print("Filter completed!")
print("Writing new file")

cleaned_log.writelines(cleaned_lines)
cleaned_log.close()

print("All done!")