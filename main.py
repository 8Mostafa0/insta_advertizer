from tkinter import ttk  # Import Treeview
import customtkinter as ctk
import tkinter as tk
import comments
import inst_api
import data
import threading
# Initialize the app


running_event = threading.Event()  # Thread-safe flag


ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

sets = inst_api.sets

app = ctk.CTk()
app.title("Insta Automation")
app.geometry("800x500")

# Numbers Part
like_number = ctk.IntVar(value=sets['max_likes'])
comment_number = ctk.IntVar(value=sets['max_comments'])
follow_number = ctk.IntVar(value=sets['max_follows'])

comment_id = ctk.IntVar(value=1)

running = False  # Variable to track function state

def save_settings(d):
    data.save_set(d)

def increase_number(var, key):
    var.set(var.get() + 1)
    sets[key] = var.get()
    save_settings(sets)

def decrease_number(var, key):
    if var.get() > 1:
        var.set(var.get() - 1)
        sets[key] = var.get()
        save_settings(sets)

# Function to create a control frame
def create_control_frame(parent, label_text, var, key):
    frame = ctk.CTkFrame(parent)
    frame.pack(pady=10, fill="both", expand=True)
    
    label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 16))
    label.pack(side="top", pady=5)
    
    button_frame = ctk.CTkFrame(frame)
    button_frame.pack(pady=5)
    
    decrease_button = ctk.CTkButton(button_frame, text="-", width=30, command=lambda: decrease_number(var, key))
    decrease_button.pack(side="left", padx=20, ipadx=10)
    
    number_label = ctk.CTkLabel(button_frame, textvariable=var, font=("Arial", 16))
    number_label.pack(side="left", padx=20, ipadx=10)
    
    increase_button = ctk.CTkButton(button_frame, text="+", width=30, command=lambda: increase_number(var, key))
    increase_button.pack(side="left", padx=20, ipadx=10)
    
    return frame

# Left-side frame for input
left_frame = ctk.CTkFrame(app)
left_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

create_control_frame(left_frame, "تعداد فالو :", follow_number, 'max_follows')
create_control_frame(left_frame, "تعداد کامنت :", comment_number, 'max_comments')
create_control_frame(left_frame, "تعداد لایک :", like_number, 'max_likes')

# Name entry section
label = ctk.CTkLabel(left_frame, text="کامنت جدیدی اضافه کنید:", font=("Arial", 16))
label.pack(pady=10)

entry = ctk.CTkEntry(left_frame, width=200, justify="right")  # Align text to the right
entry.pack(pady=10)

button = ctk.CTkButton(left_frame, text="Add to List", command=lambda: add_to_list(entry.get().strip()))
button.pack(pady=10)

# Right-side frame for listbox
right_frame = ctk.CTkFrame(app)
right_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

# Create a real Listbox (right-aligned, dark theme)
listbox = ttk.Treeview(right_frame, columns=("id", "Text"), show="headings", height=10)
listbox.heading("id", text="ایدی", anchor="center")
listbox.heading("Text", text="متن", anchor="center")

listbox.column("id", width=80, anchor="center")
listbox.column("Text", width=200, anchor="center")

listbox.pack(pady=10, padx=10, fill="both", expand=True, anchor="e")

def add_to_list(text, save: bool = True):
    if text:  # Avoid empty entries
        listbox.insert("", "end", values=(comment_id.get(), text))  # Add number + text
        comment_id.set(comment_id.get() + 1)
        if save:
            comments.save_comment(text)

def load_comments_list():
    all_comments = comments.get_comments()
    for i in all_comments:
        add_to_list(i[0], False)

load_comments_list()

def delete_selected(event):
    curItem = listbox.focus()
    selected_index = listbox.item(curItem)["values"][0] if curItem else None
    if selected_index:
        listbox.delete(curItem)
        comments.del_comment(selected_index)

listbox.bind("<Double-Button-1>", delete_selected)

logs_frame = ctk.CTkFrame(app)
logs_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

def log_message(*args):
    message = " ".join(map(str, args))
    log_box.insert("end", message + "\n")  # Append message
    log_box.see("end")  # Auto-scroll to the latest message

def run_automation():
    """Function that runs in a loop and stops when running_event is cleared."""
    while running_event.is_set():
        inst_api.start_adding(running_event,log_message)  # Repeat every 1 second

def start_stop_main_func():
    if running_event.is_set():
        running_event.clear()  # Stop the function
        lunch_bt.configure(text="شروع",fg_color="green")
        print("Function stopped.")
    else:
        running_event.set()  # Start the function
        lunch_bt.configure(text="توقف",fg_color="red")
        print("Function started.")
        threading.Thread(target=run_automation, daemon=True).start()  # Run in background

lunch_bt = ctk.CTkButton(logs_frame, text="شروع",fg_color="green", width=30, command=start_stop_main_func)
lunch_bt.pack(side="top", padx=20, ipadx=10,pady=10)

log_box = ctk.CTkTextbox(logs_frame, width=300, height=200, wrap="word")
log_box.pack(pady=10, padx=10, fill="both", expand=True)


# Run the application
app.mainloop()