import os
def find_cams(port: int):
    file = f"/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.{port}/1-1.{port}:1.0/video4linux"
    if os.path.exists(file):
        files = [int(x[5:]) for x in os.listdir(file) if x[:5] == "video" and x[5:].isnumeric()]
        files.sort()
        if len(files) > 0:
            return files[0]
for port in range(10):
    id = find_cams(port)
    if id is not None:
        print(f"{port}: {id}")