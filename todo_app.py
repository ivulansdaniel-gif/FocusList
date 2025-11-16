import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

TASKS_FILE = "tasks_advanced.json"
LOGO_FILE = "focuslist_logo.png"

class TodoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FocusList - To-Do App")
        self.root.geometry("520x600")
        self.root.resizable(True, True)
        self.root.configure(bg="#141421")
        self.tasks = []
        self.visible_indices = []  # mapping: listbox index -> self.tasks index
        self._build_ui()
        self.load_tasks()
        self.refresh_listbox()
        self.logo_img = None
        if os.path.exists(LOGO_FILE):
            try:
                self.logo_img = tk.PhotoImage(file=LOGO_FILE)
                self.root.iconphoto(True, self.logo_img)
            except Exception as e:
                print("Could not load logo:", e)

    # ---------------- UI BUILDING ---------------- #

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#141421")
        header.pack(fill="x", pady=(10, 5), padx=10)

        title_label = tk.Label(
            header,
            text="FocusList",
            font=("Arial", 20, "bold"),
            fg="#ffffff",
            bg="#141421"
        )
        title_label.pack(side="left")

        pro_button = tk.Button(
            header,
            text="Upgrade to Pro",
            font=("Arial", 10, "bold"),
            bg="#ffb347",
            fg="#141421",
            activebackground="#ffcf7e",
            activeforeground="#141421",
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            command=self.show_pro_message
        )
        pro_button.pack(side="right")

        # Input card
        input_card = tk.Frame(self.root, bg="#1f1f30", bd=0, relief="ridge")
        input_card.pack(fill="x", padx=10, pady=5, ipadx=8, ipady=8)

        # Task title
        tk.Label(
            input_card,
            text="Task",
            font=("Arial", 11),
            fg="#ffffff",
            bg="#1f1f30"
        ).grid(row=0, column=0, sticky="w")

        self.task_var = tk.StringVar()
        self.task_entry = tk.Entry(
            input_card,
            textvariable=self.task_var,
            font=("Arial", 11),
            bg="#2a2a3d",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat"
        )
        self.task_entry.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 6), ipady=3)
        input_card.grid_columnconfigure(0, weight=1)

        # Category
        tk.Label(
            input_card,
            text="Category",
            font=("Arial", 10),
            fg="#bbbbbb",
            bg="#1f1f30"
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))

        self.category_var = tk.StringVar(value="Personal")
        self.category_combo = ttk.Combobox(
            input_card,
            textvariable=self.category_var,
            values=["Work", "Study", "Personal", "Other"],
            state="readonly",
            font=("Arial", 10),
            width=12
        )
        self.category_combo.grid(row=3, column=0, sticky="w")

        # Priority
        tk.Label(
            input_card,
            text="Priority",
            font=("Arial", 10),
            fg="#bbbbbb",
            bg="#1f1f30"
        ).grid(row=2, column=1, sticky="w", pady=(4, 0), padx=(10, 0))

        self.priority_var = tk.StringVar(value="2")
        self.priority_combo = ttk.Combobox(
            input_card,
            textvariable=self.priority_var,
            values=["1", "2", "3"],  # 1 = high
            state="readonly",
            font=("Arial", 10),
            width=5
        )
        self.priority_combo.grid(row=3, column=1, sticky="w", padx=(10, 0))

        # Add button
        add_button = tk.Button(
            input_card,
            text="Add Task",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="#ffffff",
            activebackground="#66bb6a",
            activeforeground="#ffffff",
            relief="flat",
            padx=15,
            pady=5,
            command=self.add_task
        )
        add_button.grid(row=3, column=2, sticky="e", padx=(10, 0))

        # Search bar
        search_frame = tk.Frame(self.root, bg="#141421")
        search_frame.pack(fill="x", padx=10, pady=(5, 0))

        tk.Label(
            search_frame,
            text="Search:",
            font=("Arial", 10),
            fg="#cccccc",
            bg="#141421"
        ).pack(side="left")

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            bg="#1f1f30",
            fg="#ffffff",
            relief="flat",
            insertbackground="#ffffff",
            width=25
        )
        search_entry.pack(side="left", padx=(5, 0))
        search_entry.bind("<KeyRelease>", self.on_search_change)

        # Listbox card
        list_card = tk.Frame(self.root, bg="#1f1f30")
        list_card.pack(fill="both", expand=True, padx=10, pady=8)

        self.task_listbox = tk.Listbox(
            list_card,
            font=("Consolas", 11),
            bg="#1f1f30",
            fg="#ffffff",
            selectbackground="#3f51b5",
            selectforeground="#ffffff",
            activestyle="none",
            bd=0,
            highlightthickness=0
        )
        self.task_listbox.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=5)

        scrollbar = tk.Scrollbar(list_card)
        scrollbar.pack(side="right", fill="y")
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)

        # Bind double click
        self.task_listbox.bind("<Double-Button-1>", self.on_item_double_click)

        # Buttons under list
        button_frame = tk.Frame(self.root, bg="#141421")
        button_frame.pack(pady=(0, 5))

        delete_button = tk.Button(
            button_frame,
            text="Delete",
            font=("Arial", 10),
            width=12,
            bg="#e53935",
            fg="#ffffff",
            activebackground="#ef5350",
            activeforeground="#ffffff",
            relief="flat",
            command=self.delete_task
        )
        delete_button.grid(row=0, column=0, padx=5, pady=5)

        done_button = tk.Button(
            button_frame,
            text="Toggle Done",
            font=("Arial", 10),
            width=12,
            bg="#00897b",
            fg="#ffffff",
            activebackground="#26a69a",
            activeforeground="#ffffff",
            relief="flat",
            command=self.toggle_done
        )
        done_button.grid(row=0, column=1, padx=5, pady=5)

        save_button = tk.Button(
            button_frame,
            text="Save",
            font=("Arial", 10),
            width=12,
            bg="#3949ab",
            fg="#ffffff",
            activebackground="#5c6bc0",
            activeforeground="#ffffff",
            relief="flat",
            command=self.save_tasks
        )
        save_button.grid(row=0, column=2, padx=5, pady=5)

        # Stats bar
        self.stats_label = tk.Label(
            self.root,
            text="0 tasks • 0 done",
            font=("Arial", 9),
            fg="#aaaaaa",
            bg="#141421"
        )
        self.stats_label.pack(pady=(0, 8))

        # Info label
        info_label = tk.Label(
            self.root,
            text="Tip: double-click a task to toggle done.",
            font=("Arial", 8),
            fg="#777777",
            bg="#141421"
        )
        info_label.pack(pady=(0, 5))

    # ---------------- CORE LOGIC ---------------- #

    def get_selected_task_index(self):
        """Return the index in self.tasks for the currently selected row in listbox."""
        selection = self.task_listbox.curselection()
        if not selection:
            return None
        visible_index = selection[0]
        if visible_index < 0 or visible_index >= len(self.visible_indices):
            return None
        return self.visible_indices[visible_index]

    def add_task(self):
        text = self.task_var.get().strip()
        if not text:
            messagebox.showwarning("Empty task", "Write a task first, bro 😄")
            return

        category = self.category_var.get()
        priority = int(self.priority_var.get())

        new_task = {
            "text": text,
            "category": category,
            "priority": priority,
            "done": False
        }
        self.tasks.append(new_task)
        self.task_var.set("")
        self.refresh_listbox()
        self.save_tasks(auto=True)

    def delete_task(self):
        idx = self.get_selected_task_index()
        if idx is None:
            messagebox.showinfo("No selection", "Select a task to delete.")
            return

        del self.tasks[idx]
        self.refresh_listbox()
        self.save_tasks(auto=True)

    def toggle_done(self):
        idx = self.get_selected_task_index()
        if idx is None:
            messagebox.showinfo("No selection", "Select a task to toggle done.")
            return

        self.tasks[idx]["done"] = not self.tasks[idx]["done"]
        self.refresh_listbox()
        self.save_tasks(auto=True)

    def on_item_double_click(self, event):
        self.toggle_done()

    def on_search_change(self, event=None):
        query = self.search_var.get().strip().lower()
        self.refresh_listbox(query=query)

    def refresh_listbox(self, query: str = ""):
        """Refresh the list display based on tasks and search query."""
        self.task_listbox.delete(0, tk.END)
        self.visible_indices = []

        for idx, task in enumerate(self.tasks):
            text = task["text"]
            if query and (query not in text.lower()):
                continue  # filter out

            cat = task["category"]
            prio = task["priority"]
            done = task["done"]

            prefix = f"[{cat[:3].upper()}][P{prio}] "
            if done:
                prefix += "✅ "
            display_text = prefix + text

            self.visible_indices.append(idx)
            self.task_listbox.insert(tk.END, display_text)

        self.update_stats()

    def update_stats(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["done"])
        self.stats_label.config(text=f"{total} tasks • {done} done")

    # ---------------- SAVE / LOAD ---------------- #

    def save_tasks(self, auto: bool = False):
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            if not auto:
                messagebox.showinfo("Saved", "Tasks saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save tasks:\n{e}")

    def load_tasks(self):
        if not os.path.exists(TASKS_FILE):
            return
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                # basic validation
                self.tasks = []
                for t in data:
                    if not isinstance(t, dict):
                        continue
                    self.tasks.append({
                        "text": t.get("text", ""),
                        "category": t.get("category", "Other"),
                        "priority": int(t.get("priority", 2)),
                        "done": bool(t.get("done", False))
                    })
        except Exception as e:
            messagebox.showerror("Error", f"Could not load tasks:\n{e}")

    # ---------------- PRO / MONETIZATION HOOK ---------------- #

    def show_pro_message(self):
        """
        In a real app:
        - This would open a payment page (Stripe / PayPal / in-app purchase)
        - Or unlock extra features (cloud sync, themes, login, etc.)
        For now we just show a message.
        """
        messagebox.showinfo(
            "FocusList Pro",
            "In a real app this button could:\n"
            "- Open a payment page (Stripe/PayPal)\n"
            "- Unlock cloud sync & extra themes\n"
            "- Remove ads, add more features\n\n"
            "For now, it's just a demo 😉"
        )


if __name__ == "__main__":
    root = tk.Tk()
    # Use ttk theme a bit nicer
    try:
        style = ttk.Style()
        # If available, use 'clam' or 'default'
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    app = TodoApp(root)
    root.mainloop()
