import tkinter as tk
from tkinter import ttk, messagebox
import database
from datetime import datetime

class NewsApp(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("News Feed Management - Tkinter")
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self.load_all()

    def create_widgets(self):
        # Top search
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(top, text="Search (username / title / content):").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=(6,4))
        ttk.Button(top, text="Search", command=self.on_search).pack(side=tk.LEFT)
        ttk.Button(top, text="Reset", command=self.load_all).pack(side=tk.LEFT, padx=(6,0))

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Users tab
        self.tab_users = ttk.Frame(self.nb)
        self.nb.add(self.tab_users, text="Users")
        self.build_users_tab()

        # News tab
        self.tab_news = ttk.Frame(self.nb)
        self.nb.add(self.tab_news, text="News")
        self.build_news_tab()

    # Users tab
    def build_users_tab(self):
        left = ttk.Frame(self.tab_users)
        left.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(6,0), pady=6)
        cols = ("username","email","age","contact")
        self.users_tree = ttk.Treeview(left, columns=cols, show='headings', selectmode='browse')
        for c,w in (('username',140),('email',220),('age',60),('contact',140)):
            self.users_tree.heading(c, text=c.title())
            self.users_tree.column(c, width=w)
        self.users_tree.pack(fill=tk.BOTH, expand=True)
        self.users_tree.bind("<Double-1>", self.open_user_modal)

        side = ttk.Frame(self.tab_users)
        side.pack(fill=tk.Y, side=tk.LEFT, padx=8)
        ttk.Button(side, text="Add User", width=20, command=self.add_user).pack(pady=6)
        ttk.Button(side, text="Edit Selected", width=20, command=self.edit_user).pack(pady=6)
        ttk.Button(side, text="Delete Selected", width=20, command=self.delete_user).pack(pady=6)
        ttk.Button(side, text="View News", width=20, command=self.view_user_news).pack(pady=6)
        ttk.Button(side, text="Refresh", width=20, command=self.load_users).pack(pady=6)

        # add user area (compact)
        frm = ttk.Frame(side)
        frm.pack(pady=6)
        ttk.Label(frm, text="Quick add:").pack()
        self.quick_username = tk.StringVar()
        self.quick_email = tk.StringVar()
        ttk.Entry(frm, textvariable=self.quick_username, width=20).pack(pady=2)
        ttk.Entry(frm, textvariable=self.quick_email, width=20).pack(pady=2)
        ttk.Button(frm, text="Add", command=self.quick_add_user).pack(pady=2)

    def load_users(self):
        for i in self.users_tree.get_children(): self.users_tree.delete(i)
        try:
            rows = database.get_users()
            for r in rows:
                iid = f"user-{r['user_id']}"
                self.users_tree.insert('', tk.END, iid=iid, values=(r['username'], r['email'], r['age'] or '', r['contact_number'] or ''))
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def add_user(self):
        dlg = UserForm(self.root, "Add User")
        self.root.wait_window(dlg.top)
        if dlg.result:
            try:
                database.create_user(dlg.result['username'], dlg.result['email'], dlg.result['age'], dlg.result['contact'], dlg.result['bio'])
                messagebox.showinfo("Success", "User added.")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def quick_add_user(self):
        u = self.quick_username.get().strip(); e = self.quick_email.get().strip()
        if not u or not e:
            messagebox.showinfo("Input", "Enter username and email.")
            return
        try:
            database.create_user(u, e)
            self.quick_username.set(''); self.quick_email.set('')
            self.load_users()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def edit_user(self):
        sel = self.users_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a user.")
            return
        user_id = int(sel[0].split('-',1)[1])
        u = database.get_user(user_id)
        if not u:
            messagebox.showerror("Not found", "User not found.")
            return
        dlg = UserForm(self.root, "Edit User", initial=u)
        self.root.wait_window(dlg.top)
        if dlg.result:
            try:
                database.update_user(user_id, dlg.result['username'], dlg.result['email'], dlg.result['age'], dlg.result['contact'], dlg.result['bio'])
                messagebox.showinfo("Updated", "User updated.")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_user(self):
        sel = self.users_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a user.")
            return
        user_id = int(sel[0].split('-',1)[1])
        if not messagebox.askyesno("Confirm", "Delete user and all their news?"):
            return
        try:
            database.delete_user(user_id)
            messagebox.showinfo("Deleted", "User deleted.")
            self.load_users(); self.load_news()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_user_modal(self, event=None):
        sel = self.users_tree.selection()
        if not sel: return
        user_id = int(sel[0].split('-',1)[1])
        u = database.get_user(user_id)
        if not u:
            messagebox.showerror("Not found", "User not found.")
            return
        dlg = UserModal(self.root, u, refresh_cb=self.load_all)
        self.root.wait_window(dlg.top)

    def view_user_news(self):
        sel = self.users_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a user.")
            return
        user_id = int(sel[0].split('-',1)[1])
        u = database.get_user(user_id)
        dlg = UserModal(self.root, u, refresh_cb=self.load_all)
        self.root.wait_window(dlg.top)

    # News tab
    def build_news_tab(self):
        left = ttk.Frame(self.tab_news)
        left.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(6,0), pady=6)
        cols = ("title","username","created_at")
        self.news_tree = ttk.Treeview(left, columns=cols, show='headings', selectmode='browse')
        for c,w in (('title',400),('username',180),('created_at',140)):
            self.news_tree.heading(c, text=c.title())
            self.news_tree.column(c, width=w)
        self.news_tree.pack(fill=tk.BOTH, expand=True)
        self.news_tree.bind("<Double-1>", self.show_news_content)

        side = ttk.Frame(self.tab_news)
        side.pack(fill=tk.Y, side=tk.LEFT, padx=8)
        ttk.Button(side, text="Add News", width=20, command=self.add_news).pack(pady=6)
        ttk.Button(side, text="Edit Selected", width=20, command=self.edit_news).pack(pady=6)
        ttk.Button(side, text="Delete Selected", width=20, command=self.delete_news).pack(pady=6)
        ttk.Button(side, text="Refresh", width=20, command=self.load_news).pack(pady=6)

    def load_news(self):
        for i in self.news_tree.get_children(): self.news_tree.delete(i)
        try:
            rows = database.get_news()
            for r in rows:
                iid = f"news-{r['news_id']}"
                created = r['created_at'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r['created_at'],'strftime') else str(r['created_at'])
                self.news_tree.insert('', tk.END, iid=iid, values=(r['title'], r['username'], created))
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def add_news(self):
        users = database.get_users()
        if not users:
            messagebox.showinfo("No users", "Create a user before adding news.")
            return
        dlg = NewsForm(self.root, "Add News", users=users)
        self.root.wait_window(dlg.top)
        if dlg.result:
            try:
                database.create_news(dlg.result['title'], dlg.result['body'], dlg.result['user_id'], dlg.result['username'])
                messagebox.showinfo("Created", "News created.")
                self.load_news()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_news(self):
        sel = self.news_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select news to edit.")
            return
        news_id = int(sel[0].split('-',1)[1])
        n = database.get_single_news(news_id)
        if not n:
            messagebox.showerror("Not found", "News not found.")
            return
        dlg = NewsEditForm(self.root, "Edit News", initial=n)
        self.root.wait_window(dlg.top)
        if dlg.result:
            try:
                database.update_news(news_id, dlg.result['title'], dlg.result['body'])
                messagebox.showinfo("Updated", "News updated.")
                self.load_news()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_news(self):
        sel = self.news_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select news to delete.")
            return
        news_id = int(sel[0].split('-',1)[1])
        if not messagebox.askyesno("Confirm", "Delete this news?"):
            return
        try:
            database.delete_news(news_id)
            messagebox.showinfo("Deleted", "News deleted.")
            self.load_news()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_news_content(self, event):
        sel = self.news_tree.selection()
        if not sel: return
        news_id = int(sel[0].split('-',1)[1])
        n = database.get_single_news(news_id)
        if n:
            messagebox.showinfo(n['title'], n['body'])

    # Search
    def on_search(self):
        q = self.search_var.get().strip()
        if not q:
            self.load_all(); return
        try:
            users, news = database.search_all(q)
            # populate users
            for i in self.users_tree.get_children(): self.users_tree.delete(i)
            for r in users:
                iid = f"user-{r['user_id']}"
                self.users_tree.insert('', tk.END, iid=iid, values=(r['username'], r['email'], r['age'] or '', r['contact_number'] or ''))
            # populate news
            for i in self.news_tree.get_children(): self.news_tree.delete(i)
            for r in news:
                iid = f"news-{r['news_id']}"
                created = r['created_at'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r['created_at'],'strftime') else str(r['created_at'])
                self.news_tree.insert('', tk.END, iid=iid, values=(r['title'], r['username'], created))
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def load_all(self):
        self.load_users()
        self.load_news()

# -------- Dialogs and forms --------
class UserForm:
    def __init__(self, parent, title, initial=None):
        self.top = tk.Toplevel(parent)
        self.top.transient(parent); self.top.grab_set()
        self.top.title(title)
        self.result = None

        frm = ttk.Frame(self.top, padding=10); frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Username:").grid(row=0,column=0, sticky=tk.W); self.username = tk.StringVar(value=(initial['username'] if initial else '')); ttk.Entry(frm, textvariable=self.username, width=40).grid(row=0,column=1,pady=4)
        ttk.Label(frm, text="Email:").grid(row=1,column=0, sticky=tk.W); self.email = tk.StringVar(value=(initial['email'] if initial else '')); ttk.Entry(frm, textvariable=self.email, width=40).grid(row=1,column=1,pady=4)
        ttk.Label(frm, text="Age:").grid(row=2,column=0, sticky=tk.W); self.age = tk.StringVar(value=(str(initial['age']) if initial and initial.get('age') is not None else '')); ttk.Entry(frm, textvariable=self.age, width=10).grid(row=2,column=1,sticky=tk.W,pady=4)
        ttk.Label(frm, text="Contact:").grid(row=3,column=0, sticky=tk.W); self.contact = tk.StringVar(value=(initial['contact_number'] if initial else '')); ttk.Entry(frm, textvariable=self.contact, width=40).grid(row=3,column=1,pady=4)
        ttk.Label(frm, text="Bio:").grid(row=4,column=0, sticky=tk.NW); self.bio = tk.Text(frm, height=6, width=40); self.bio.grid(row=4,column=1,pady=4)
        if initial and initial.get('bio'): self.bio.insert('1.0', initial['bio'])

        btns = ttk.Frame(frm); btns.grid(row=5,column=0,columnspan=2,pady=(8,0))
        ttk.Button(btns, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT)

    def on_ok(self):
        try:
            age_val = int(self.age.get()) if self.age.get().strip()!='' else None
        except ValueError:
            messagebox.showerror("Input", "Age must be integer"); return
        if not self.username.get().strip() or not self.email.get().strip():
            messagebox.showerror("Input", "Username and email required"); return
        self.result = {
            'username': self.username.get().strip(),
            'email': self.email.get().strip(),
            'age': age_val,
            'contact': self.contact.get().strip(),
            'bio': self.bio.get('1.0','end').strip()
        }
        self.top.destroy()

class NewsForm:
    def __init__(self, parent, title, users):
        self.top = tk.Toplevel(parent)
        self.top.transient(parent); self.top.grab_set()
        self.top.title(title)
        self.result = None

        frm = ttk.Frame(self.top, padding=10); frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Author:").grid(row=0,column=0, sticky=tk.W)
        self.user_map = {f"{u['username']} ({u['email']})": u for u in users}
        self.author_var = tk.StringVar(); combo = ttk.Combobox(frm, values=list(self.user_map.keys()), textvariable=self.author_var, width=50); combo.grid(row=0,column=1,pady=4)
        if users: combo.set(list(self.user_map.keys())[0])
        ttk.Label(frm, text="Title:").grid(row=1,column=0, sticky=tk.W); self.title = tk.StringVar(); ttk.Entry(frm, textvariable=self.title, width=60).grid(row=1,column=1,pady=4)
        ttk.Label(frm, text="Body:").grid(row=2,column=0, sticky=tk.NW); self.body = tk.Text(frm, width=60, height=12); self.body.grid(row=2,column=1,pady=4)

        btns = ttk.Frame(frm); btns.grid(row=3,column=0,columnspan=2,pady=(8,0))
        ttk.Button(btns, text="Publish", command=self.on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT)

    def on_ok(self):
        key = self.author_var.get().strip()
        if not key: messagebox.showerror("Input","Select author"); return
        user = self.user_map.get(key)
        title = self.title.get().strip(); body = self.body.get('1.0','end').strip()
        if not title or not body: messagebox.showerror("Input","Title and body required"); return
        self.result = {'title': title, 'body': body, 'user_id': user['user_id'], 'username': user['username']}
        self.top.destroy()

class NewsEditForm:
    def __init__(self, parent, title, initial):
        self.top = tk.Toplevel(parent)
        self.top.transient(parent); self.top.grab_set()
        self.top.title(title)
        self.result = None
        frm = ttk.Frame(self.top, padding=10); frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Title:").grid(row=0,column=0, sticky=tk.W); self.title = tk.StringVar(value=initial['title']); ttk.Entry(frm, textvariable=self.title, width=60).grid(row=0,column=1,pady=4)
        ttk.Label(frm, text="Body:").grid(row=1,column=0, sticky=tk.NW); self.body = tk.Text(frm, width=60, height=14); self.body.grid(row=1,column=1,pady=4); self.body.insert('1.0', initial['body'])
        btns = ttk.Frame(frm); btns.grid(row=2,column=0,columnspan=2,pady=(8,0)); ttk.Button(btns, text="Save", command=self.on_ok).pack(side=tk.LEFT, padx=4); ttk.Button(btns, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT)

    def on_ok(self):
        title = self.title.get().strip(); body = self.body.get('1.0','end').strip()
        if not title or not body: messagebox.showerror("Input", "Title and body required"); return
        self.result = {'title': title, 'body': body}
        self.top.destroy()

class UserModal:
    def __init__(self, parent, user, refresh_cb=None):
        self.parent = parent; self.user = user; self.refresh_cb = refresh_cb
        self.top = tk.Toplevel(parent); self.top.transient(parent); self.top.grab_set()
        self.top.title(f"User: {user['username']}")
        self.top.geometry("900x500")
        frame = ttk.Frame(self.top, padding=8); frame.pack(fill=tk.BOTH, expand=True)

        info = ttk.Frame(frame); info.pack(fill=tk.X, padx=4, pady=4)
        ttk.Label(info, text=f"{user['username']} — {user['email']}", font=('TkDefaultFont',12,'bold')).pack(side=tk.LEFT)
        ttk.Button(info, text="Edit User", command=self.edit_user).pack(side=tk.RIGHT, padx=4)
        ttk.Button(info, text="Delete User", command=self.delete_user).pack(side=tk.RIGHT)

        # news list
        self.news_tree = ttk.Treeview(frame, columns=('title','created_at'), show='headings', selectmode='browse')
        self.news_tree.heading('title', text='Title'); self.news_tree.heading('created_at', text='Created At')
        self.news_tree.column('title', width=620); self.news_tree.column('created_at', width=200)
        self.news_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(4,0), pady=6)
        self.news_tree.bind("<Double-1>", self.show_news)

        side = ttk.Frame(frame); side.pack(fill=tk.Y, side=tk.LEFT, padx=8)
        ttk.Button(side, text="Add News", width=20, command=self.add_news).pack(pady=6)
        ttk.Button(side, text="Edit Selected", width=20, command=self.edit_selected_news).pack(pady=6)
        ttk.Button(side, text="Delete Selected", width=20, command=self.delete_selected_news).pack(pady=6)
        ttk.Button(side, text="Refresh", width=20, command=self.load_news).pack(pady=6)
        ttk.Button(side, text="Close", width=20, command=self.top.destroy).pack(pady=6)

        self.load_news()

    def load_news(self):
        for i in self.news_tree.get_children(): self.news_tree.delete(i)
        rows = database.get_news_by_user(self.user['user_id'])
        for r in rows:
            iid = f"news-{r['news_id']}"
            created = r['created_at'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r['created_at'],'strftime') else str(r['created_at'])
            self.news_tree.insert('', tk.END, iid=iid, values=(r['title'], created))

    def add_news(self):
        dlg = NewsForm(self.parent, "Add News", users=[self.user])
        self.parent.wait_window(dlg.top)
        if dlg.result:
            try:
                database.create_news(dlg.result['title'], dlg.result['body'], dlg.result['user_id'], dlg.result['username'])
                messagebox.showinfo("Created", "News created.")
                self.load_news(); 
                if self.refresh_cb: self.refresh_cb()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_selected_news(self):
        sel = self.news_tree.selection()
        if not sel: messagebox.showinfo("Select", "Select news"); return
        news_id = int(sel[0].split('-',1)[1])
        n = database.get_single_news(news_id)
        dlg = NewsEditForm(self.parent, "Edit News", initial=n)
        self.parent.wait_window(dlg.top)
        if dlg.result:
            try:
                database.update_news(news_id, dlg.result['title'], dlg.result['body'])
                messagebox.showinfo("Updated", "News updated."); self.load_news(); 
                if self.refresh_cb: self.refresh_cb()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_selected_news(self):
        sel = self.news_tree.selection()
        if not sel: messagebox.showinfo("Select", "Select news"); return
        news_id = int(sel[0].split('-',1)[1])
        if not messagebox.askyesno("Confirm", "Delete news?"): return
        try:
            database.delete_news(news_id); messagebox.showinfo("Deleted","News deleted."); self.load_news(); 
            if self.refresh_cb: self.refresh_cb()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_user(self):
        u = database.get_user(self.user['user_id'])
        dlg = UserForm(self.parent, "Edit User", initial=u)
        self.parent.wait_window(dlg.top)
        if dlg.result:
            try:
                database.update_user(self.user['user_id'], dlg.result['username'], dlg.result['email'], dlg.result['age'], dlg.result['contact'], dlg.result['bio'])
                messagebox.showinfo("Updated", "User updated.")
                if self.refresh_cb: self.refresh_cb()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_user(self):
        if not messagebox.askyesno("Confirm","Delete user and all their news?"): return
        try:
            database.delete_user(self.user['user_id']); messagebox.showinfo("Deleted","User deleted."); 
            if self.refresh_cb: self.refresh_cb(); self.top.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_news(self, event):
        sel = self.news_tree.selection()
        if not sel: return
        news_id = int(sel[0].split('-',1)[1])
        n = database.get_single_news(news_id)
        if n: messagebox.showinfo(n['title'], n['body'])

# --------- Run ----------
def main():
    root = tk.Tk()
    root.geometry("1100x700")
    NewsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()