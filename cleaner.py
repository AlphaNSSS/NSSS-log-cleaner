filter = ["Unknown console command."]

raw_log = open('server.log', 'r')
cleaned_log = open('cleaned.log', 'w')

raw_lines = raw_log.readlines()
cleaned_lines = []

for line in raw_lines:
    for item in filter:
        if not line.__contains__(item):
            cleaned_lines.append(line)

cleaned_log.writelines(cleaned_lines)
cleaned_log.close()