# NSSS log cleaner

Can't find something in the log file for your NSSS Minecraft server because of irrelevant spam?<br>
This little script filters out all unnecessary system messages so you can focus on player activity.

**NOTE:** This utility was intended for Minecraft servers running on NSSS 1.1.11_111-1

## How to use

When run, the script will ask for the file path of the log file to clean. The script will take the contents of that file and put it into the newly generated *cleaned.log*.

**TIP:** Put the log file into the same directory as the script, that way you only have to write the file name and not the full path. You will be prompted for the path anyways, just ignore that. Just write the name.

**Example:** *server.log* and the script are in the same directory, just enter "server.log" when prompted for a path.

## Custom Filters

The script uses the contents of *filter.json* to filter out any unwanted messages. If the contents of a line in that file matches even a small part of log line, the log line is binned. You can add your own filters onto the default assortment by copy-pasting certain parts of lines you want to remove.

**WARNING:** When adding filters, make sure that they are not too short or include phrases that may appear in chat messages. If they do, the chat messages will be filtered out.

## Further customization / Note on incompleteness

Unfortuntely there's easy way to customize the look of the cleaned log files. If you really want to, go in and modify the archaic script I made in a day. It's really messy because it was originally for personal use, but I might make customization easier in the future (probably not). If you have any suggestions for how the logs could be formatted better, let me know by opening an issue on this repo!

If you find any inconsistencies in the cleaned log file, it's probably because of edge cases that weren't filtered out or accounted for in my formatting. This was really just a personal project and I had a single 333203 line long log file to clean up. I don't know how your server differs from the one where my log originates from, but if you think I missed something make sure to open an issue and let me know.