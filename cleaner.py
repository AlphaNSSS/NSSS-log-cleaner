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
    "/51.15.34.47",
    "/70.188.165.60",
    "/70.188.165.60",
]

print("Opening files...")

raw_log = open('server.log', 'r')
cleaned_log = open('cleaned.log', 'w')

raw_lines = raw_log.readlines()
cleaned_lines = []

print("Begin filtration")

found_illegal = False
day_timestamp = ""
for line in raw_lines:
    # check if the line should be filtered out
    for item in filter:
        if line.lower().__contains__(item.lower()):
            found_illegal = True

    # what should be done if it's not filtered out
    if not found_illegal:
        if day_timestamp != line[:10]:
            day_timestamp = line[:10]
            cleaned_lines.append("================================{}================================\n".format(day_timestamp))


        edit_str = line[11:]
        edit_str = edit_str.replace("[INFO]", "|")
        cleaned_lines.append(edit_str)

    found_illegal = False

print("Filter completed!")
print("Writing new file")

cleaned_log.writelines(cleaned_lines)
cleaned_log.close()

print("All done!")