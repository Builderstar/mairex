import subprocess, uuid

class Shell:
	def __init__(self):
		self.proc = subprocess.Popen(
		["bash"], stdin=subprocess.PIPE,
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
		text=True, bufsize=1, errors='replace')

	def run(self, cmd) -> str:
		sentinel = f"__DONE_{uuid.uuid4().hex}__"
		self.proc.stdin.write(f"{cmd}\necho {sentinel}\n")
		self.proc.stdin.flush()
		lines = []
		for line in self.proc.stdout:
			if sentinel in line:
				break
			lines.append(line)
		return "".join(lines)

	def close(self):
		self.proc.stdin.close()
		self.proc.wait()
