# Modified PromptManager.py using ttk.Treeview

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os

class PromptManagerApp(tk.Tk):
    PROMPT_FILENAME = "promptData.json"

    def __init__(self):
        super().__init__()
        self.title("Prompt Manager")
        self.geometry("600x450")

        self.prompt_directory = None
        self.prompts = {}
        self.current_prompt_name = None

        self.main_frame = ttk.Frame(self)
        self.create_prompt_frame = ttk.Frame(self)
        self.view_edit_frame = ttk.Frame(self)

        self.frames = {
            "main": self.main_frame,
            "create": self.create_prompt_frame,
            "view_edit": self.view_edit_frame,
        }

        self.setup_main_screen()
        self.setup_create_prompt_screen()
        self.setup_view_edit_screen()

        self.switch_frame("main")
        self.load_prompts()

    def switch_frame(self, frame_name):
        for name, frame in self.frames.items():
            if name == frame_name:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    # --- Directory and File Handling Logic (Unchanged from previous correct version) ---
    def _get_full_prompt_path(self):
        if self.prompt_directory:
            return os.path.join(self.prompt_directory, self.PROMPT_FILENAME)
        return None

    def select_directory_and_load(self):
        dir_path = filedialog.askdirectory(
            title="Select Directory Containing (or to contain) promptData.json"
        )
        if dir_path:
            self.prompt_directory = dir_path
            self.load_prompts()
        else:
            messagebox.showinfo("Info", "Directory selection cancelled.")

    def load_prompts(self):
        if not self.prompt_directory:
            messagebox.showinfo("Setup Required", "Please select a directory to store your prompts.")
            self.select_directory_and_load()
            if not self.prompt_directory:
                messagebox.showwarning("Warning", "No directory selected. Cannot load or save prompts.")
                self.prompts = {}
                self.update_prompt_list()
                return

        target_file_path = self._get_full_prompt_path()
        if not target_file_path:
             messagebox.showerror("Internal Error", "Prompt directory is set but path couldn't be constructed.")
             self.prompts = {}
             self.update_prompt_list()
             return

        self.prompts = {}
        file_exists = os.path.exists(target_file_path)
        load_successful = False
        create_new_file = False

        if file_exists:
            try:
                with open(target_file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.prompts = data
                        load_successful = True
                    else:
                        messagebox.showwarning("Warning", f"File '{self.PROMPT_FILENAME}' found but has an unexpected format (expected a JSON dictionary).")
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Error decoding JSON file '{self.PROMPT_FILENAME}'. It might be corrupted.")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading prompts from '{self.PROMPT_FILENAME}': {e}")

        if not load_successful:
            prompt_message = ""
            if file_exists:
                 prompt_message = f"Could not load prompts from '{self.PROMPT_FILENAME}' in the selected directory.\n\nDo you want to create a new (or overwrite the existing) '{self.PROMPT_FILENAME}' file here?"
            else:
                 prompt_message = f"File '{self.PROMPT_FILENAME}' not found in the selected directory.\n\nDo you want to create it now?"

            if messagebox.askyesno("Create Prompt File?", prompt_message, parent=self):
                create_new_file = True
            else:
                messagebox.showinfo("Info", "Proceeding without loading or creating a prompt file.")
                create_new_file = False

        if create_new_file:
            self.prompts = {}
            try:
                self.save_prompts()
                messagebox.showinfo("File Created", f"New file '{self.PROMPT_FILENAME}' created successfully in '{self.prompt_directory}'.")
            except Exception as e:
                 messagebox.showerror("Creation Failed", f"Failed to create '{self.PROMPT_FILENAME}'. Error: {e}")

        self.update_prompt_list()

    def save_prompts(self):
        target_file_path = self._get_full_prompt_path()
        if target_file_path:
            try:
                os.makedirs(self.prompt_directory, exist_ok=True)
                with open(target_file_path, 'w') as f:
                    json.dump(self.prompts, f, indent=4)
            except Exception as e:
                messagebox.showerror("Error", f"Error saving prompts to '{target_file_path}': {e}")
        else:
            messagebox.showwarning("Warning", "No prompt directory selected. Cannot save prompts. Please select a directory first.")

    # --- UI Setup and Logic (Adjusted for Treeview) ---

    def setup_main_screen(self):
        main_frame = self.main_frame
        main_frame.columnconfigure(0, weight=1) # Make treeview column expandable
        main_frame.rowconfigure(2, weight=1) # Make treeview row expandable

        ttk.Label(main_frame, text="Saved Prompts", font=('Arial', 14)).grid(row=0, column=0, pady=(10,0), sticky='w', padx=10)

        self.file_path_label = ttk.Label(main_frame, text="Directory: None Selected", wraplength=580, anchor='w', justify=tk.LEFT)
        self.file_path_label.grid(row=1, column=0, pady=(0, 5), padx=10, sticky='ew')

        # --- Treeview Setup ---
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, pady=5, padx=10, sticky='nsew')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        self.prompt_tree = ttk.Treeview(
            tree_frame,
            columns=('Prompt Name',),
            show='headings', # Don't show the default '#' column
            yscrollcommand=tree_scroll.set,
            selectmode='browse' # Only allow selecting one item
        )
        tree_scroll.config(command=self.prompt_tree.yview)

        # Define headings
        self.prompt_tree.heading('Prompt Name', text='Prompt Name')
        self.prompt_tree.column('Prompt Name', anchor='w') # Stretch not needed if only one column

        self.prompt_tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll.grid(row=0, column=1, sticky='ns')

        # Bind double-click to view/edit
        self.prompt_tree.bind("<Double-1>", self.view_selected_prompt)
        # Update button states on selection change
        self.prompt_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        # --- End Treeview Setup ---


        # --- Action Buttons Frame ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=10)

        self.view_edit_button = ttk.Button(button_frame, text="View/Edit", command=self.view_selected_prompt, state=tk.DISABLED)
        self.view_edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_selected_prompt, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="New Prompt", command=self.go_to_create_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Select Directory", command=self.select_directory_and_load).pack(side=tk.LEFT, padx=5) # Renamed for clarity


    def on_tree_select(self, event=None):
        """Enable/disable buttons based on Treeview selection."""
        selected_items = self.prompt_tree.selection()
        if selected_items: # If something is selected
            self.view_edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.view_edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)

    def _get_selected_prompt_name(self):
        """Helper to get the name of the currently selected prompt in the Treeview."""
        selected_items = self.prompt_tree.selection()
        if not selected_items:
            # messagebox.showinfo("Information", "Please select a prompt from the list first.")
            return None
        # Get the first (and only, due to 'browse' mode) selected item identifier
        item_id = selected_items[0]
        # Retrieve the value associated with the 'Prompt Name' column for that item
        item_data = self.prompt_tree.item(item_id)
        # Depending on how data is inserted, it might be in 'text' or 'values'
        # We inserted using values=(name,), so it should be in values[0]
        if 'values' in item_data and item_data['values']:
             return item_data['values'][0]
        # Fallback if inserted differently (less likely with current code)
        elif 'text' in item_data:
             return item_data['text']
        return None # Should not happen if selection exists


    def update_prompt_list(self):
        """ Updates the Treeview and the directory path label """
        if self.prompt_directory:
            display_path = f"Directory: {self.prompt_directory}\nFile: {self.PROMPT_FILENAME}"
            self.file_path_label.config(text=display_path)
        else:
            self.file_path_label.config(text="Directory: None Selected")

        # Clear previous items in the Treeview
        if self.prompt_tree.winfo_exists():
            for item in self.prompt_tree.get_children():
                self.prompt_tree.delete(item)

            # Populate Treeview
            if not self.prompts:
                # Optionally display a message *in* the tree (less common)
                # self.prompt_tree.insert('', tk.END, text="No prompts found or loaded.", tags=('empty',))
                # self.prompt_tree.tag_configure('empty', foreground='grey')
                # Or just leave it empty and rely on button states
                pass
            else:
                sorted_prompt_names = sorted(self.prompts.keys())
                for name in sorted_prompt_names:
                    # Insert item, using the name for both the display and the value
                    self.prompt_tree.insert('', tk.END, values=(name,))

        # Update button states after list update
        self.on_tree_select()


    # --- Methods using Treeview selection ---

    def view_selected_prompt(self, event=None): # Accept event for binding
        """Handles View/Edit button click or double-click."""
        prompt_name = self._get_selected_prompt_name()
        if prompt_name:
            self.view_prompt_body(prompt_name)
        elif event: # Only show message if triggered by event (not direct call)
             messagebox.showinfo("Information", "Please select a prompt from the list to view/edit.")


    def delete_selected_prompt(self):
        """Handles Delete button click."""
        prompt_name = self._get_selected_prompt_name()
        if prompt_name:
            self.delete_prompt(prompt_name) # Call the existing delete logic
        else:
             messagebox.showinfo("Information", "Please select a prompt from the list to delete.")

    # --- Other methods mostly unchanged, but ensure they call update_prompt_list ---

    def go_to_create_prompt(self):
        if not self.prompt_directory:
            messagebox.showwarning("Directory Required", "Please select a prompt directory before creating new prompts.")
            self.select_directory_and_load()
            if not self.prompt_directory:
                return
        self.switch_frame("create")
        self.clear_create_prompt_fields()

    def setup_create_prompt_screen(self):
        # (Setup remains the same visually)
        create_frame = self.create_prompt_frame
        ttk.Label(create_frame, text="Create New Prompt", font=('Arial', 14)).pack(pady=10)

        ttk.Label(create_frame, text="Name:").pack(pady=(10,0))
        self.create_name_entry = ttk.Entry(create_frame, width=60)
        self.create_name_entry.pack(pady=5, padx=20)

        ttk.Label(create_frame, text="Body:").pack(pady=(10,0))
        body_frame = ttk.Frame(create_frame)
        body_frame.pack(pady=5, padx=20, fill="both", expand=True)
        body_scrollbar = tk.Scrollbar(body_frame)
        body_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.create_body_text = tk.Text(body_frame, height=10, width=50, wrap=tk.WORD, yscrollcommand=body_scrollbar.set)
        self.create_body_text.pack(side=tk.LEFT, fill="both", expand=True)
        body_scrollbar.config(command=self.create_body_text.yview)

        button_frame = ttk.Frame(create_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Save", command=self.save_new_prompt).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_create_prompt).pack(side=tk.LEFT, padx=10)

    def clear_create_prompt_fields(self):
        self.create_name_entry.delete(0, tk.END)
        self.create_body_text.delete("1.0", tk.END)

    def save_new_prompt(self):
        if not self.prompt_directory:
             messagebox.showerror("Error", "Cannot save prompt. No directory selected.")
             return

        name = self.create_name_entry.get().strip()
        body = self.create_body_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Validation Error", "Prompt name cannot be empty.")
            return
        if not body:
            messagebox.showerror("Validation Error", "Prompt body cannot be empty.")
            return

        if name in self.prompts:
            if not messagebox.askyesno("Overwrite Confirmation", f"Prompt name '{name}' already exists. Overwrite it?"):
                 return

        self.prompts[name] = body
        self.save_prompts()
        self.update_prompt_list() # Refresh the Treeview
        self.switch_frame("main")

    def cancel_create_prompt(self):
        name = self.create_name_entry.get().strip()
        body = self.create_body_text.get("1.0", tk.END).strip()
        if name or body:
            if messagebox.askyesno("Confirmation", "Are you sure you want to cancel? Unsaved changes will be lost."):
                self.switch_frame("main")
        else:
             self.switch_frame("main")

    def view_prompt_body(self, prompt_name): # Now called with name from selection handlers
        if not self.prompt_directory or prompt_name not in self.prompts:
             messagebox.showerror("Error", f"Prompt '{prompt_name}' not found or directory not loaded.")
             self.update_prompt_list()
             return

        self.current_prompt_name = prompt_name # Still useful for edit screen logic
        self.view_edit_name_label.config(text=f"Viewing/Editing: {prompt_name}")
        self.view_edit_body_text.config(state=tk.NORMAL)
        self.view_edit_body_text.delete("1.0", tk.END)
        self.view_edit_body_text.insert("1.0", self.prompts[prompt_name])
        self.view_edit_body_text.config(state=tk.DISABLED)
        self.edit_body_button.config(text="Edit Body")
        self.rename_button.config(state=tk.NORMAL) # Rename button on view screen
        self.save_body_button.pack_forget()
        self.edit_body_button.pack(side=tk.LEFT, padx=5) # Ensure edit button is shown
        self.editing_body = False
        self.switch_frame("view_edit")

    def setup_view_edit_screen(self):
        # (Setup remains the same visually)
        view_edit_frame = self.view_edit_frame

        self.view_edit_name_label = ttk.Label(view_edit_frame, text="Viewing/Editing: Prompt Name", font=('Arial', 14), wraplength=580)
        self.view_edit_name_label.pack(pady=10, padx=10, anchor='w')

        body_frame = ttk.Frame(view_edit_frame)
        body_frame.pack(pady=5, padx=20, fill="both", expand=True)
        body_scrollbar = tk.Scrollbar(body_frame)
        body_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.view_edit_body_text = tk.Text(body_frame, height=15, width=60, wrap=tk.WORD, state=tk.DISABLED, yscrollcommand=body_scrollbar.set)
        self.view_edit_body_text.pack(side=tk.LEFT, fill="both", expand=True)
        body_scrollbar.config(command=self.view_edit_body_text.yview)

        button_frame = ttk.Frame(view_edit_frame)
        button_frame.pack(pady=10)

        self.edit_body_button = ttk.Button(button_frame, text="Edit Body", command=self.toggle_edit_body)
        self.edit_body_button.pack(side=tk.LEFT, padx=5)

        self.save_body_button = ttk.Button(button_frame, text="Save Body Changes", command=self.save_edited_body)

        self.rename_button = ttk.Button(button_frame, text="Rename Prompt", command=self.edit_prompt_name_from_view)
        self.rename_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Return to List", command=self.return_to_main_screen_from_view).pack(side=tk.LEFT, padx=5)

        # --- NEW: Copy Prompt Button ---
        self.copy_prompt_button = ttk.Button(button_frame, text="Copy Prompt", command=self.copy_prompt_to_clipboard)
        self.copy_prompt_button.pack(side=tk.LEFT, padx=5)
        # --- End NEW: Copy Prompt Button ---

        self.editing_body = False

    # --- NEW: Copy Prompt to Clipboard Function ---
    def copy_prompt_to_clipboard(self):
        if self.current_prompt_name and self.current_prompt_name in self.prompts:
            prompt_body = self.prompts[self.current_prompt_name]
            formatted_prompt = f"FOLLOW THIS SYSTEM PROMPT: [ {prompt_body} ] SYSTEM PROMPT OVER. "
            self.clipboard_clear()
            self.clipboard_append(formatted_prompt)
            self.update() # Needed on some systems to make clipboard work immediately
            messagebox.showinfo("Copied", "Prompt copied to clipboard!")
        else:
            messagebox.showerror("Error", "No prompt selected or prompt not found.")
    # --- End NEW: Copy Prompt to Clipboard Function ---


    def toggle_edit_body(self):
        if not self.editing_body:
            self.view_edit_body_text.config(state=tk.NORMAL)
            self.edit_body_button.pack_forget()
            self.save_body_button.pack(side=tk.LEFT, padx=5)
            self.rename_button.config(state=tk.DISABLED)
            self.copy_prompt_button.config(state=tk.DISABLED) # Disable copy button during edit
            self.view_edit_body_text.focus_set()
            self.editing_body = True
        else: # This 'else' was missing in the original code for toggle_edit_body. Added for completeness, though not directly related to the new feature.
            self.view_edit_body_text.config(state=tk.DISABLED) # Re-disable if toggling off edit mode without saving (hypothetical scenario from button logic point of view)
            self.save_body_button.pack_forget() # Hide save button again if toggling off edit mode
            self.edit_body_button.pack(side=tk.LEFT, padx=5) # Show edit button again
            self.rename_button.config(state=tk.NORMAL) # Re-enable rename
            self.copy_prompt_button.config(state=tk.NORMAL) # Re-enable copy button
            self.editing_body = False # Ensure editing_body flag is set correctly if toggling off

    def save_edited_body(self):
        if not self.prompt_directory:
             messagebox.showerror("Error", "Cannot save changes. No directory selected.")
             return

        # Use self.current_prompt_name which was set when view_prompt_body was called
        if self.current_prompt_name and self.editing_body:
            new_body = self.view_edit_body_text.get("1.0", tk.END).strip()
            if not new_body:
                 messagebox.showerror("Validation Error", "Prompt body cannot be empty.")
                 return

            self.prompts[self.current_prompt_name] = new_body
            self.save_prompts()
            self.view_edit_body_text.config(state=tk.DISABLED)
            self.save_body_button.pack_forget()
            self.edit_body_button.pack(side=tk.LEFT, padx=5)
            self.rename_button.config(state=tk.NORMAL)
            self.copy_prompt_button.config(state=tk.NORMAL) # Re-enable copy button after save
            self.editing_body = False
            messagebox.showinfo("Success", f"Prompt '{self.current_prompt_name}' body updated.")
        elif not self.current_prompt_name:
            messagebox.showerror("Error", "Internal error: No prompt name tracked for saving body.")


    def return_to_main_screen_from_view(self):
        if self.editing_body:
             original_body = ""
             if self.current_prompt_name in self.prompts:
                 original_body = self.prompts[self.current_prompt_name]
             current_body_text = self.view_edit_body_text.get("1.0", tk.END).strip()

             if current_body_text != original_body:
                 if messagebox.askyesno("Confirmation", "You have unsaved changes to the body. Return to list and discard changes?"):
                     self.editing_body = False
                     self.switch_frame("main")
                 else:
                     return
             else:
                 self.editing_body = False
                 self.switch_frame("main")
        else:
            self.switch_frame("main")

    def edit_prompt_name_from_view(self):
         # Use self.current_prompt_name which was set when view_prompt_body was called
         if not self.prompt_directory:
             messagebox.showerror("Error", "Cannot rename prompt. No directory selected.")
             return
         if self.current_prompt_name and not self.editing_body:
             self.edit_prompt_name(self.current_prompt_name) # Call the rename logic
         elif self.editing_body:
             messagebox.showinfo("Info", "Please save or cancel body edits before renaming.")
         elif not self.current_prompt_name:
              messagebox.showerror("Error", "Internal error: No prompt selected to rename.")


    # edit_prompt_name remains largely the same, but gets called differently
    def edit_prompt_name(self, old_name):
        if not self.prompt_directory:
             messagebox.showerror("Error", "Cannot rename prompt. No directory selected.")
             return
        if old_name not in self.prompts:
             messagebox.showerror("Error", "Cannot rename - prompt no longer exists.")
             self.update_prompt_list()
             return

        edit_name_dialog = tk.Toplevel(self)
        edit_name_dialog.title("Edit Prompt Name")
        edit_name_dialog.geometry("350x150")

        ttk.Label(edit_name_dialog, text=f"Current Name: {old_name}").pack(pady=5)
        ttk.Label(edit_name_dialog, text="New Name:").pack(pady=5)
        new_name_entry = ttk.Entry(edit_name_dialog, width=45)
        new_name_entry.pack(pady=5, padx=10)
        new_name_entry.insert(0, old_name)
        new_name_entry.select_range(0, tk.END)
        new_name_entry.focus_set()

        def save_new_name():
            new_name = new_name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Validation Error", "Prompt name cannot be empty.", parent=edit_name_dialog)
                return
            if new_name == old_name:
                edit_name_dialog.destroy()
                return
            if new_name in self.prompts:
                messagebox.showerror("Validation Error", f"Prompt name '{new_name}' already exists.", parent=edit_name_dialog)
                return

            body = self.prompts.pop(old_name)
            self.prompts[new_name] = body
            self.save_prompts()
            self.update_prompt_list() # Update the Treeview

            # If the renamed prompt was the one being viewed, update the view screen's state
            if self.current_prompt_name == old_name:
                self.current_prompt_name = new_name
                # Update label only if the view/edit screen is currently active
                if self.view_edit_frame.winfo_ismapped():
                     self.view_edit_name_label.config(text=f"Viewing/Editing: {new_name}")


            edit_name_dialog.destroy()
            messagebox.showinfo("Success", f"Prompt renamed to '{new_name}'.")

        button_frame = ttk.Frame(edit_name_dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Save Name", command=save_new_name).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=edit_name_dialog.destroy).pack(side=tk.LEFT, padx=10)

        edit_name_dialog.transient(self)
        edit_name_dialog.grab_set()
        self.wait_window(edit_name_dialog)

    # delete_prompt remains largely the same, but gets called differently
    def delete_prompt(self, name): # Name is passed by delete_selected_prompt
        if not self.prompt_directory:
             messagebox.showerror("Error", "Cannot delete prompt. No directory selected.")
             return
        if name not in self.prompts:
             # This might happen if selection changes between clicking delete and confirmation
             messagebox.showerror("Error", "Cannot delete - prompt no longer exists or selection changed.")
             self.update_prompt_list()
             return

        if messagebox.askyesno("Confirmation", f"Are you sure you want to delete the prompt '{name}'?"):
            del self.prompts[name]
            self.save_prompts()
            self.update_prompt_list() # Update the Treeview

            # If deleting the currently viewed prompt, return to main screen
            # Check if view screen is active and name matches
            if self.view_edit_frame.winfo_ismapped() and self.current_prompt_name == name:
                self.switch_frame("main")
                self.current_prompt_name = None
            elif self.current_prompt_name == name:
                # Clear tracking variable even if view wasn't active
                self.current_prompt_name = None


if __name__ == "__main__":
    app = PromptManagerApp()
    app.mainloop()