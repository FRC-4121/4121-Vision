import os


# How does this work? I have no idea!
def find_cams(port: int):
    port = int(port)
    port4 = [2, 1, 4, 3][port]
    # Pi 4
    file = f"/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.{port4}/1-1.{port4}:1.0/video4linux"
    if os.path.exists(file):
        files = [
            int(x[5:])
            for x in os.listdir(file)
            if x[:5] == "video" and x[5:].isnumeric()
        ]
        files.sort()
        if len(files) > 0:
            return files[0]
    # Pi 5
    port5 = [0, 1, 3, 2][port]
    file = "/sys/devices/platform/axi/1000120000.pcie/1f00{0}00000.usb/xhci-hcd.{1}/usb{2}/{2}-{3}/{2}-{3}:1.0/video4linux".format(
        port5 % 2 + 2, port5 % 2, port5 % 2 * 2 + 1, port5 // 2 + 1
    )
    if os.path.exists(file):
        files = [
            int(x[5:])
            for x in os.listdir(file)
            if x[:5] == "video" and x[5:].isnumeric()
        ]
        files.sort()
        if len(files) > 0:
            return files[0]


for port in range(4):
    id = find_cams(port)
    if id is not None:
        print(f"{port}: {id}")
