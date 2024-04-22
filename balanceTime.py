from datetime import timedelta

timeList = ('-125:33', '-1:01', '1:02')
def balanceStrHM(*arg):
    mysum = timedelta()

    for i in arg:
        (h, m) = i.split(':')
        if i.startswith('-'):
            d = timedelta(hours = int(h), minutes = -int(m))
        else:
            d = timedelta(hours=int(h), minutes=int(m))
        mysum += d
    total_seconds = mysum.total_seconds()
    if mysum < timedelta(0):
        hours = str(int(-total_seconds // 3600)).zfill(2)
        minutes = str(int((-total_seconds % 3600) // 60)).zfill(2)
        return f"-{hours}:{minutes}"
    else:
        hours = str(int(total_seconds // 3600)).zfill(2)
        minutes = str(int((total_seconds % 3600) // 60)).zfill(2)
        return f"{hours}:{minutes}"

print(balanceStrHM(*timeList))


