import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# -----------------------------------------------------------
# DATABASE CONNECTION
# -----------------------------------------------------------
def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # CHANGE THIS
        password="",       # CHANGE THIS
        database="news_db"
    )

# -----------------------------------------------------------
# USERS CRUD FUNCTIONS
# -----------------------------------------------------------
def create_user(username, email, age, contact, bio):
    conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO Users (username,email,age,contact_number,bio) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(query, (username, email, age, contact, bio))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_users():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def update_user(user_id, username, email, age, contact, bio):
    conn = connect()
    cursor = conn.cursor()
    query = "UPDATE Users SET username=%s,email=%s,age=%s,contact_number=%s,bio=%s WHERE user_id=%s"
    cursor.execute(query, (username, email, age, contact, bio, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_user(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE user_id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

# -----------------------------------------------------------
# NEWS CRUD FUNCTIONS
# -----------------------------------------------------------
def create_news(title, body, user_id, username):
    conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO News (title, body, user_id, username) VALUES (%s,%s,%s,%s)"
    cursor.execute(query, (title, body, user_id, username))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_news():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM News")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def update_news(news_id, title, body):
    conn = connect()
    cursor = conn.cursor()
    query = "UPDATE News SET title=%s, body=%s WHERE news_id=%s"
    cursor.execute(query, (title, body, news_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_news(news_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM News WHERE news_id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()

# -----------------------------------------------------------
# GUI APPLICATION
# -----------------------------------------------------------
class CRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("News & Users CRUD App")
        self.root.geometry("900x600")

        self.tab_control = ttk.Notebook(root)
        
        # USERS TAB
        self.tab_users = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_users, text="Users")
        self.create_users_tab()

        # NEWS TAB
        self.tab_news = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_news, text="News")
        self.create_news_tab()

        self.tab_control.pack(expand=1, fill="both")

    # -------------------------------------------------------
    # USERS TAB GUI
    # -------------------------------------------------------
    def create_users_tab(self):
        # Labels
        labels = ["Username", "Email", "Age", "Contact", "Bio"]
        for i, text in enumerate(labels):
            tk.Label(self.tab_users, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")

        # Entry fields
        self.user_entries = {}
        for i, key in enumerate(["username","email","age","contact","bio"]):
            self.user_entries[key] = tk.Entry(self.tab_users, width=30)
            self.user_entries[key].grid(row=i, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(self.tab_users, text="Add User", command=self.add_user).grid(row=0,column=2,padx=10)
        tk.Button(self.tab_users, text="Update User", command=self.update_user_btn).grid(row=1,column=2,padx=10)
        tk.Button(self.tab_users, text="Delete User", command=self.delete_user_btn).grid(row=2,column=2,padx=10)
        tk.Button(self.tab_users, text="Refresh List", command=self.load_users).grid(row=3,column=2,padx=10)

        # Treeview
        self.user_tree = ttk.Treeview(self.tab_users, columns=("ID","Username","Email","Age","Contact","Bio"), show="headings")
        for col in self.user_tree["columns"]:
            self.user_tree.heading(col, text=col)
        self.user_tree.grid(row=6, column=0, columnspan=3, pady=10, sticky="nsew")

        self.user_tree.bind("<ButtonRelease-1>", self.fill_user_entries)
        self.load_users()

    def load_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        for user in get_all_users():
            self.user_tree.insert("", "end", values=user)

    def add_user(self):
        try:
            create_user(
                self.user_entries["username"].get(),
                self.user_entries["email"].get(),
                int(self.user_entries["age"].get()),
                self.user_entries["contact"].get(),
                self.user_entries["bio"].get()
            )
            messagebox.showinfo("Success", "User Added")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def fill_user_entries(self, event):
        selected = self.user_tree.focus()
        if selected:
            values = self.user_tree.item(selected)["values"]
            self.selected_user_id = values[0]
            self.user_entries["username"].delete(0, tk.END)
            self.user_entries["username"].insert(0, values[1])
            self.user_entries["email"].delete(0, tk.END)
            self.user_entries["email"].insert(0, values[2])
            self.user_entries["age"].delete(0, tk.END)
            self.user_entries["age"].insert(0, values[3])
            self.user_entries["contact"].delete(0, tk.END)
            self.user_entries["contact"].insert(0, values[4])
            self.user_entries["bio"].delete(0, tk.END)
            self.user_entries["bio"].insert(0, values[5])

    def update_user_btn(self):
        try:
            update_user(
                self.selected_user_id,
                self.user_entries["username"].get(),
                self.user_entries["email"].get(),
                int(self.user_entries["age"].get()),
                self.user_entries["contact"].get(),
                self.user_entries["bio"].get()
            )
            messagebox.showinfo("Success", "User Updated")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_user_btn(self):
        try:
            delete_user(self.selected_user_id)
            messagebox.showinfo("Success", "User Deleted")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -------------------------------------------------------
    # NEWS TAB GUI
    # -------------------------------------------------------
    def create_news_tab(self):
        # Labels
        labels = ["Title", "Body", "User ID", "Username"]
        for i, text in enumerate(labels):
            tk.Label(self.tab_news, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")

        # Entry fields
        self.news_entries = {}
        for i, key in enumerate(["title","body","user_id","username"]):
            self.news_entries[key] = tk.Entry(self.tab_news, width=40)
            self.news_entries[key].grid(row=i, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(self.tab_news, text="Add News", command=self.add_news).grid(row=0,column=2,padx=10)
        tk.Button(self.tab_news, text="Update News", command=self.update_news_btn).grid(row=1,column=2,padx=10)
        tk.Button(self.tab_news, text="Delete News", command=self.delete_news_btn).grid(row=2,column=2,padx=10)
        tk.Button(self.tab_news, text="Refresh List", command=self.load_news).grid(row=3,column=2,padx=10)

        # Treeview
        self.news_tree = ttk.Treeview(self.tab_news, columns=("ID","Title","Body","Created","UserID","Username"), show="headings")
        for col in self.news_tree["columns"]:
            self.news_tree.heading(col, text=col)
        self.news_tree.grid(row=6, column=0, columnspan=3, pady=10, sticky="nsew")

        self.news_tree.bind("<ButtonRelease-1>", self.fill_news_entries)
        self.load_news()

    def load_news(self):
        for row in self.news_tree.get_children():
            self.news_tree.delete(row)
        for news in get_all_news():
            self.news_tree.insert("", "end", values=news)

    def add_news(self):
        try:
            create_news(
                self.news_entries["title"].get(),
                self.news_entries["body"].get(),
                int(self.news_entries["user_id"].get()),
                self.news_entries["username"].get()
            )
            messagebox.showinfo("Success", "News Added")
            self.load_news()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def fill_news_entries(self, event):
        selected = self.news_tree.focus()
        if selected:
            values = self.news_tree.item(selected)["values"]
            self.selected_news_id = values[0]
            self.news_entries["title"].delete(0, tk.END)
            self.news_entries["title"].insert(0, values[1])
            self.news_entries["body"].delete(0, tk.END)
            self.news_entries["body"].insert(0, values[2])
            self.news_entries["user_id"].delete(0, tk.END)
            self.news_entries["user_id"].insert(0, values[4])
            self.news_entries["username"].delete(0, tk.END)
            self.news_entries["username"].insert(0, values[5])

    def update_news_btn(self):
        try:
            update_news(
                self.selected_news_id,
                self.news_entries["title"].get(),
                self.news_entries["body"].get()
            )
            messagebox.showinfo("Success", "News Updated")
            self.load_news()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_news_btn(self):
        try:
            delete_news(self.selected_news_id)
            messagebox.showinfo("Success", "News Deleted")
            self.load_news()
        except Exception as e:
            messagebox.showerror("Error", str(e))

# -----------------------------------------------------------
# RUN APPLICATION
# -----------------------------------------------------------
root = tk.Tk()
app = CRUDApp(root)
root.mainloop()
