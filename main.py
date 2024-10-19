import tkinter as tk
import wexpect  # Use wexpect for Windows compatibility
import threading
import time

def start_steamcmd():
    global child
    child = wexpect.spawn('steamcmd')
    child.logfile = None
    read_thread = threading.Thread(target=read_output)
    read_thread.daemon = True
    read_thread.start()

def read_output():
    while True:
        try:
            line = child.readline().strip()  # Read each line from the steamcmd output
            if line:
                append_output(line + '\n')
        except wexpect.EOF:
            append_output('Child process exited.')
            break

def append_output(output_text):
    text_output.insert(tk.END, output_text)
    text_output.see(tk.END)

def send_command():
    command = entry.get()
    if command:
        try:
            # Wait for SteamCMD to be ready before sending the command
            child.expect('Steam>', timeout=None)
            child.sendline(command)
            time.sleep(0.5)  # Add a small delay to ensure the command is processed correctly
            entry.delete(0, tk.END)
        except wexpect.TIMEOUT:
            append_output('Error: Timeout while waiting for SteamCMD prompt. Command not sent.\n')
        except wexpect.ExceptionPexpect as e:
            append_output(f'Error: {str(e)}\n')

def on_closing():
    if child.isalive():
        child.close()
    root.destroy()

# Create the GUI application
root = tk.Tk()
root.title("SteamCMD Interactive Shell")
root.geometry("600x400")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Create text widget to display steamcmd output
text_output = tk.Text(frame, wrap=tk.WORD, height=20, state=tk.NORMAL)
text_output.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Entry widget for command input
entry = tk.Entry(root, width=100)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Bind Enter key to send command
entry.bind('<Return>', lambda event: send_command())

# Start steamcmd and read output in a background thread
start_steamcmd()

# Handle window close event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the Tkinter main loop
root.mainloop()
