import subprocess, time

out = subprocess.run(["/Users/dustin/.local/bin/nlm", "create", "notebook", "Audio Test Notebook"], capture_output=True, text=True)
print(out.stdout)
nid = out.stdout.split("ID: ")[1].strip()

out2 = subprocess.run(["/Users/dustin/.local/bin/nlm", "source", "add", nid, "--url", "https://ko.wikipedia.org/wiki/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5", "--wait"], capture_output=True, text=True)
print("Source added")

out3 = subprocess.run(["/Users/dustin/.local/bin/nlm", "audio", "create", nid, "--confirm"], capture_output=True, text=True)
print(out3.stdout)

for _ in range(5):
    out4 = subprocess.run(["/Users/dustin/.local/bin/nlm", "studio", "status", nid], capture_output=True, text=True)
    print("STATUS:", out4.stdout)
    time.sleep(10)
