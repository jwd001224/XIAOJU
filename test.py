import HSyslog

test = 0
while True:
    if test < 10:
        HSyslog.log_info(str(test))
        test += 1
    else:
        test = 0
