import shlex

EMULATED_DIRECTORIES = {
    "home": {
        "user": {}
    },
    "var": {
        "log": {}
    },
    "etc": {},
    "tmp": {}
}

class Shell(object):
    def __init__(self, channel, username, addr, logfile):
        self.channel = channel
        self.ip = addr[0] or 'unknown'
        self.command_history = []
        self.username = username
        self.logfile = logfile
        self.current_dir = ["home", "user"]
        self.init_log_file()

    def start(self):
        self.channel.send(b"bastion$ ")
        command = b""
        while True:
            char = self.channel.recv(1)
            if not char:
                self.channel.close()
                break
            if char == b'\r':
                self.channel.send(b"\r\n")
                self.log_command(command.decode().strip())
                response = self._handle_command(command.strip().decode())
                self.channel.send(response)
                self.channel.send(b"bastion$ ")
                command = b""
            elif char == b'\x7f':  # Handle backspace (ASCII DEL)
                if command:
                    command = command[:-1]
                    self.channel.send(b'\b \b')
            else:
                self.channel.send(char)
                command += char

    def _handle_command(self, command):
        parts = shlex.split(command)
        if not parts:
            return b""

        cmd = parts[0]
        args = parts[1:]

        if cmd == 'exit':
            self.channel.send(b"Goodbye!\r\n")
            self.channel.close()
            return b""
        elif cmd == 'pwd':
            return f"\n{'/'.join(self.current_dir)}/\r\n".encode()
        elif cmd == 'cd':
            response, self.current_dir = change_directory(args, self.current_dir)
            return response
        elif cmd == 'ls':
            return list_directories(args, self.current_dir)
        elif cmd == 'cat':
            return cat(args, self.current_dir)
        else:
            return f"bash: {command}: command not found\r\n".encode()

    def log_command(self, command):
        with open(self.logfile, "a") as log:
            log.write(f"{self.username}@bastion$ {command}\n")

    def init_log_file(self):
        with open(self.logfile, "a") as log:
            log.write(f"{self.ip}\n")
def list_directories(args, current_dir):
    try:
        directory = EMULATED_DIRECTORIES
        for dir in current_dir:
            directory = directory.get(dir, {})
        files = directory.keys()
        if not '-a' in args or '-la' in args:
            files = [f for f in files if not f.startswith('.')]
        if '-l' in args or '-la' in args:
            file_info = []
            for file in files:
                if isinstance(directory[file], dict):
                    file_type = 'd'
                else:
                    file_type = '-'
                file_info.append(f"{file_type} {file}")
            return "\r\n".join(file_info).encode() + b"\r\n"
        else:
            return " ".join(files).encode() + b"\r\n"
    except KeyError:
        return b"ls: cannot access\r\n"

def cat(args, current_dir):
    if not args:
        return b"cat: missing argument\r\n"
    directory = EMULATED_DIRECTORIES
    for dir in current_dir:
        directory = directory.get(dir, {})
    file_content = directory.get(args[0], None)
    if isinstance(file_content, str):
        return file_content.encode() + b"\r\n"
    else:
        return b"cat: no such file\r\n"

def change_directory(args, current_dir):
    if not args:
        return b"cd: missing argument\r\n", current_dir
    if args[0] == "..":
        if current_dir != [""]:
            current_dir.pop()
    elif args[0] in EMULATED_DIRECTORIES:
        current_dir.append(args[0])
    elif len(current_dir) == 1 and args[0] in EMULATED_DIRECTORIES[current_dir[0]]:
        current_dir.append(args[0])
    elif len(current_dir) == 2 and args[0] in EMULATED_DIRECTORIES[current_dir[0]][current_dir[1]]:
        current_dir.append(args[0])
    else:
        return b"cd: no such file or directory\r\n", current_dir

    return b"", current_dir
