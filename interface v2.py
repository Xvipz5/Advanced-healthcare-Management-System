import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime

class Authenticator:
    def __init__(self, user_data_file):
        self.user_data_file = user_data_file
        self.users = self.load_users()

    def load_users(self):
        """Loads user data from an Excel file."""
        try:
            df = pd.read_excel(self.user_data_file)
            return {row['Username']: row['Password'] for index, row in df.iterrows()}
        except FileNotFoundError:
            print(f"Error: The file {self.user_data_file} does not exist.")
            return {}

    def validate_user(self, username, password):
        """Validates a user's credentials."""
        return self.users.get(username) == password

    def register_user(self, username, password):
        """Registers a new user and saves it to the Excel file."""
        if username in self.users:
            return False, "Username already exists."

        # Append the new user to the Excel file
        df = pd.read_excel(self.user_data_file)
        new_user = pd.DataFrame([[username, password]], columns=['Username', 'Password'])
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_excel(self.user_data_file, index=False)

        # Update the internal users dictionary
        self.users[username] = password
        return True, "Registration successful."


class LoginScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("500x350")
        self.center_window(self.root, 500, 350)
        self.root.configure(bg='white')

        self.authenticator = Authenticator('/Users/benoi/Downloads/ExecFinal/users.xlsx')

        self.setup_gui()

    def setup_gui(self):
        frame = tk.Frame(self.root, bg='white')
        frame.pack(expand=True, padx=20, pady=20)

        tk.Label(frame, text="Healthcare Management System", font=('Arial', 18, 'bold'), bg='white', fg='black').pack(pady=20)

        username_frame = tk.Frame(frame, bg='white')
        username_frame.pack(pady=5)
        tk.Label(username_frame, text="Username:", font=('Arial', 12), bg='white', fg='black').pack(side=tk.LEFT)
        self.username_entry = tk.Entry(username_frame, font=('Arial', 12), width=30, bg='white', fg='black')
        self.username_entry.pack(side=tk.LEFT, padx=10)

        password_frame = tk.Frame(frame, bg='white')
        password_frame.pack(pady=5)
        tk.Label(password_frame, text="Password:", font=('Arial', 12), bg='white', fg='black').pack(side=tk.LEFT)
        self.password_entry = tk.Entry(password_frame, show="*", font=('Arial', 12), width=30, bg='white', fg='black')
        self.password_entry.pack(side=tk.LEFT, padx=10)

        self.login_button = tk.Button(frame, text="Login", command=self.login, font=('Arial', 12), bg='#dcdcdc', fg='black', width=15)
        self.login_button.pack(pady=10)

        self.register_button = tk.Button(frame, text="Register", command=self.open_registration_window, font=('Arial', 12), bg='#dcdcdc', fg='black', width=15)
        self.register_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.authenticator.validate_user(username, password):
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.open_main_application()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_main_application(self):
        self.root.destroy()

        main_menu = tk.Tk()
        main_menu.title("Main Menu")
        main_menu.geometry("600x500")
        self.center_window(main_menu, 600, 500)
        main_menu.configure(bg='#f0f0f0')

        tk.Label(main_menu, text="Healthcare Management System - Main Menu", font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='black').pack(pady=20)

        tk.Button(main_menu, text="Schedule", command=self.open_schedule, font=('Arial', 14), bg='#dcdcdc', fg='black', width=20).pack(pady=10)
        tk.Button(main_menu, text="Patient Records", command=self.open_patient_records, font=('Arial', 14), bg='#dcdcdc', fg='black', width=20).pack(pady=10)
        tk.Button(main_menu, text="Staff Directory", command=self.open_staff_directory, font=('Arial', 14), bg='#dcdcdc', fg='black', width=20).pack(pady=10)

        tk.Button(main_menu, text="Back", command=lambda: self.back_to_login(main_menu), font=('Arial', 14), bg='#dcdcdc', fg='black', width=20).pack(pady=10)

        main_menu.mainloop()

    def back_to_login(self, current_window):
        """Closes the current window and reopens the login screen."""
        current_window.destroy()
        self.__init__()  # Reinitialize the login screen

    def open_schedule(self):
        schedule_window = tk.Toplevel()
        schedule_window.title("Schedule")
        schedule_window.geometry("800x600")
        self.center_window(schedule_window, 800, 600)
        schedule_window.configure(bg='white')

        tk.Label(schedule_window, text="Schedule", font=('Arial', 16, 'bold'), bg='white', fg='black').pack(pady=10)

        # Create a Treeview to display the schedule
        tree = ttk.Treeview(schedule_window, columns=('Patient Name', 'Appointment Time', 'Urgency'), show='headings')
        tree.heading('Patient Name', text='Patient Name')
        tree.heading('Appointment Time', text='Appointment Time')
        tree.heading('Urgency', text='Urgency')

        # Style for Treeview
        style = ttk.Style()
        style.configure('Treeview', font=('Arial', 12), foreground='black', background='white')
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'), foreground='white', background='black')

        # Read the Excel file and process data
        try:
            df = pd.read_excel('/Users/benoi/Downloads/ExecFinal/healthcare_records.xlsx')

            # Convert and sort the data by date and time
            df['Appointment Date'] = pd.to_datetime(df['Appointment Time']).dt.date
            df['Appointment Time'] = pd.to_datetime(df['Appointment Time'])
            df = df.sort_values(by=['Appointment Date', 'Appointment Time'])

            # Insert data into Treeview grouped by date
            current_date = None
            for index, row in df.iterrows():
                appointment_date = row['Appointment Date']
                if appointment_date != current_date:
                    # Add a blank row for spacing before the date
                    tree.insert('', tk.END, values=('', '', ''))

                    current_date = appointment_date
                    tree.insert('', tk.END, values=(current_date.strftime('%B %d, %Y'), '', ''), tags=('date',))

                full_name = f"{row['First Name']} {row['Last Name']}"
                appointment_time = row['Appointment Time'].strftime('%I:%M %p')
                urgency_level = row['Urgency']
                tree.insert('', tk.END, values=(full_name, appointment_time, urgency_level), iid=str(index))

        except FileNotFoundError:
            messagebox.showerror("Error", "The schedule file was not found.")
        except KeyError as e:
            messagebox.showerror("Error", f"Missing column in the file: {e}")

        # Configure date row with black text
        tree.tag_configure('date', font=('Arial', 12, 'bold'), foreground='black', background='#d9edf7')
        tree.pack(expand=True, fill='both', padx=20, pady=20)

        # Function to open the record details
        def open_record():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a record to view.")
                return

            # Get the index of the selected item
            item_index = int(selected_item[0])
            record = df.iloc[item_index]

            # Create a new window to display the details
            record_window = tk.Toplevel(schedule_window)
            record_window.title("Record Details")
            record_window.geometry("400x300")
            self.center_window(record_window, 400, 300)
            record_window.configure(bg='white')

            # Display the record details
            tk.Label(record_window, text=f"Patient: {record['First Name']} {record['Last Name']}", font=('Arial', 14), bg='white', fg='black').pack(pady=10)
            tk.Label(record_window, text=f"Health Card Number: {record['Health Card Number']}", font=('Arial', 12), bg='white', fg='black').pack(pady=5)
            tk.Label(record_window, text=f"Description: {record['Brief Description']}", font=('Arial', 12), bg='white', fg='black').pack(pady=5)

        # Add open record button
        open_record_button = tk.Button(schedule_window, text="Open Record", command=open_record, font=('Arial', 12), bg='#dcdcdc', fg='black', width=15)
        open_record_button.pack(side=tk.RIGHT, padx=20, pady=10)

        # Add back button
        back_button = tk.Button(schedule_window, text="Back", command=schedule_window.destroy, font=('Arial', 12), bg='#dcdcdc', fg='black', width=15)
        back_button.pack(side=tk.LEFT, padx=20, pady=10)

    def open_patient_records(self):
        records_window = tk.Toplevel()
        records_window.title("Patient Records")
        records_window.geometry("950x650")
        self.center_window(records_window, 950, 650)
        records_window.configure(bg='white')

        tk.Label(records_window, text="Patient Records", font=('Arial', 16, 'bold'), bg='white', fg='black').pack(pady=10)

        # Search bar
        search_frame = tk.Frame(records_window, bg='white')
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search by Patient Name:", font=('Arial', 12), bg='white', fg='black').pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame, font=('Arial', 12), width=30, bg='white', fg='black')
        search_entry.pack(side=tk.LEFT, padx=5)

        # Create a Treeview to display the patient records
        tree = ttk.Treeview(records_window, columns=('Patient Name', 'Health Card Number', 'Appointment Date', 'Condition', 'Solution'), show='headings')
        tree.heading('Patient Name', text='Patient Name')
        tree.heading('Health Card Number', text='Health Card Number')
        tree.heading('Appointment Date', text='Appointment Date')
        tree.heading('Condition', text='Condition')
        tree.heading('Solution', text='Solution')

        # Style for Treeview
        style = ttk.Style()
        style.configure('Treeview', font=('Arial', 12), foreground='black', background='white')
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'), foreground='white', background='black')

        # Read the Excel file and process data
        try:
            df = pd.read_excel('/Users/benoi/Downloads/ExecFinal/past_patient_records.xlsx')
            df['Appointment Date'] = pd.to_datetime(df['Appointment Time']).dt.strftime('%Y-%m-%d %I:%M %p')
            df['Patient Name'] = df['First Name'] + ' ' + df['Last Name']

            # Insert data into Treeview
            def populate_treeview(data_frame):
                for _, row in data_frame.iterrows():
                    tree.insert('', tk.END, values=(row['Patient Name'], row['Health Card Number'], row['Appointment Date'], row['Brief Description'], row['Solution']))

            populate_treeview(df)

            # Search function to filter results
            def search():
                query = search_entry.get().lower()
                # Clear current rows
                for row in tree.get_children():
                    tree.delete(row)
                # Filter DataFrame based on query
                filtered_df = df[df['Patient Name'].str.lower().str.contains(query)]
                populate_treeview(filtered_df)

        except FileNotFoundError:
            messagebox.showerror("Error", "The patient records file was not found.")
        except KeyError as e:
            messagebox.showerror("Error", f"Missing column in the file: {e}")

        search_button = tk.Button(search_frame, text="Search", command=search, font=('Arial', 12), bg='#dcdcdc', fg='black')
        search_button.pack(side=tk.LEFT, padx=5)

        tree.pack(expand=True, fill='both', padx=20, pady=20)

        # Add back button
        back_button = tk.Button(records_window, text="Back", command=records_window.destroy, font=('Arial', 12), bg='#dcdcdc', fg='black', width=15)
        back_button.pack(pady=10)

    def open_staff_directory(self):
        directory_window = tk.Toplevel()
        directory_window.title("Staff Directory")
        directory_window.geometry("1000x700")
        self.center_window(directory_window, 1000, 700)
        directory_window.configure(bg='white')

        tk.Label(directory_window, text="Staff Directory", font=('Arial', 16, 'bold'), bg='white', fg='black').pack(pady=10)

        # Search bar
        search_frame = tk.Frame(directory_window, bg='white')
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search by Name:", font=('Arial', 12), bg='white', fg='black').pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame, font=('Arial', 12), width=30, bg='white', fg='black')
        search_entry.pack(side=tk.LEFT, padx=5)

        # Create a Treeview to display the staff directory
        tree = ttk.Treeview(directory_window, columns=('First Name', 'Last Name', 'Employee ID', 'Occupation', 'Schedule Days', 'Schedule Times', 'Status'), show='headings')

        # Configure column widths to better fit the content
        tree.column('First Name', width=120, anchor='center')
        tree.column('Last Name', width=120, anchor='center')
        tree.column('Employee ID', width=120, anchor='center')
        tree.column('Occupation', width=120, anchor='center')
        tree.column('Schedule Days', width=200, anchor='center')
        tree.column('Schedule Times', width=150, anchor='center')
        tree.column('Status', width=100, anchor='center')

        tree.heading('First Name', text='First Name')
        tree.heading('Last Name', text='Last Name')
        tree.heading('Employee ID', text='Employee ID')
        tree.heading('Occupation', text='Occupation')
        tree.heading('Schedule Days', text='Schedule Days')
        tree.heading('Schedule Times', text='Schedule Times')
        tree.heading('Status', text='Status')

        # Style for Treeview
        style = ttk.Style()
        style.configure('Treeview', font=('Arial', 12), foreground='black', background='white')
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'), foreground='white', background='black')

        # Read the Excel file and process data
        try:
            df = pd.read_excel('/Users/benoi/Downloads/ExecFinal/staff_directory.xlsx')

            # Insert data into Treeview
            def populate_treeview(data_frame):
                for _, row in data_frame.iterrows():
                    tree.insert('', tk.END, values=(row['First Name'], row['Last Name'], row['Employee ID'], row['Occupation'], row['Schedule Days'], row['Schedule Times'], row['Status']))

            populate_treeview(df)

            # Search function to filter results
            def search():
                query = search_entry.get().lower()
                # Clear current rows
                for row in tree.get_children():
                    tree.delete(row)
                # Filter DataFrame based on query
                filtered_df = df[df['First Name'].str.lower().str.contains(query) | df['Last Name'].str.lower().str.contains(query)]
                populate_treeview(filtered_df)

        except FileNotFoundError:
            messagebox.showerror("Error", "The staff directory file was not found.")
        except KeyError as e:
            messagebox.showerror("Error", f"Missing column in the file: {e}")

        search_button = tk.Button(search_frame, text="Search", command=search, font=('Arial', 12), bg='#dcdcdc', fg='black')
        search_button.pack(side=tk.LEFT, padx=5)

        tree.pack(expand=True, fill='both', padx=20, pady=20)

        # Add back button
        back_button = tk.Button(directory_window, text="Back", command=directory_window.destroy, font=('Arial', 12), bg='#dcdcdc', fg='black', width=15)
        back_button.pack(pady=10)

    def open_registration_window(self):
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Register")
        reg_window.geometry("400x350")
        self.center_window(reg_window, 400, 350)
        reg_window.configure(bg='white')

        tk.Label(reg_window, text="Register New User", font=('Arial', 16, 'bold'), bg='white', fg='black').pack(pady=20)

        # Username entry
        tk.Label(reg_window, text="Username:", font=('Arial', 12), bg='white', fg='black').pack(pady=5)
        username_entry = tk.Entry(reg_window, font=('Arial', 12), width=30, bg='white', fg='black')
        username_entry.pack(pady=5)

        # Password entry
        tk.Label(reg_window, text="Password:", font=('Arial', 12), bg='white', fg='black').pack(pady=5)
        password_entry = tk.Entry(reg_window, show="*", font=('Arial', 12), width=30, bg='white', fg='black')
        password_entry.pack(pady=5)

        # Confirm Password entry
        tk.Label(reg_window, text="Confirm Password:", font=('Arial', 12), bg='white', fg='black').pack(pady=5)
        confirm_password_entry = tk.Entry(reg_window, show="*", font=('Arial', 12), width=30, bg='white', fg='black')
        confirm_password_entry.pack(pady=5)

        def register():
            username = username_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()

            if not username or not password:
                messagebox.showerror("Error", "Username and Password cannot be empty.")
                return

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match.")
                return

            success, message = self.authenticator.register_user(username, password)
            if success:
                messagebox.showinfo("Success", message)
                reg_window.destroy()
            else:
                messagebox.showerror("Error", message)

        tk.Button(reg_window, text="Add User", command=register, font=('Arial', 12), bg='#dcdcdc', fg='black', width=15).pack(pady=20)

    def center_window(self, window, width, height):
        """Centers a window on the screen."""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def run(self):
        self.root.mainloop()


def main():
    app = LoginScreen()
    app.run()

if __name__ == "__main__":
    main()
