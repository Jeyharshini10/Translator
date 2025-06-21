import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import pyperclip
import pyttsx3
import threading
from googletrans import Translator, LANGUAGES
import concurrent.futures
from typing import Dict, Optional

class LanguageTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Language Translation Tool")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize translator
        self.translator = Translator()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        # Language mappings
        self.languages = LANGUAGES
        self.language_list = [(code, name.title()) for code, name in self.languages.items()]
        self.language_list.sort(key=lambda x: x[1])
        
        # Variables
        self.source_lang = tk.StringVar(value='auto')
        self.target_lang = tk.StringVar(value='en')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Language Translation Tool", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Language selection frame
        lang_frame = ttk.LabelFrame(main_frame, text="Language Selection", padding="10")
        lang_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        lang_frame.columnconfigure(1, weight=1)
        lang_frame.columnconfigure(3, weight=1)
        
        # Source language
        ttk.Label(lang_frame, text="From:").grid(row=0, column=0, padx=(0, 10))
        self.source_combo = ttk.Combobox(lang_frame, textvariable=self.source_lang, 
                                        width=20, state="readonly")
        self.source_combo.grid(row=0, column=1, padx=(0, 20), sticky=(tk.W, tk.E))
        
        # Swap button
        swap_btn = ttk.Button(lang_frame, text="⇄", width=3, 
                             command=self.swap_languages)
        swap_btn.grid(row=0, column=2, padx=5)
        
        # Target language
        ttk.Label(lang_frame, text="To:").grid(row=0, column=3, padx=(20, 10))
        self.target_combo = ttk.Combobox(lang_frame, textvariable=self.target_lang, 
                                        width=20, state="readonly")
        self.target_combo.grid(row=0, column=4, sticky=(tk.W, tk.E))
        
        # Populate comboboxes
        self.populate_language_combos()
        
        # Input text frame
        input_frame = ttk.LabelFrame(main_frame, text="Input Text", padding="10")
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                        pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        # Input text area
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, width=70,
                                                   font=('Arial', 11), wrap=tk.WORD)
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input buttons frame
        input_btn_frame = ttk.Frame(input_frame)
        input_btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Clear input button
        clear_input_btn = ttk.Button(input_btn_frame, text="Clear", 
                                    command=self.clear_input)
        clear_input_btn.pack(side=tk.LEFT, padx=(0, 10))
    
        # Paste button
        paste_btn = ttk.Button(input_btn_frame, text="Paste", 
                              command=self.paste_text)
        paste_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Translate button
        self.translate_btn = ttk.Button(input_btn_frame, text="Translate", 
                                       command=self.translate_text, style='Accent.TButton')
        self.translate_btn.pack(side=tk.RIGHT)
        
        # Output text frame
        output_frame = ttk.LabelFrame(main_frame, text="Translation", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, width=70,
                                                    font=('Arial', 11), wrap=tk.WORD,
                                                    state='disabled')
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Output buttons frame
        output_btn_frame = ttk.Frame(output_frame)
        output_btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Copy button
        copy_btn = ttk.Button(output_btn_frame, text="Copy", 
                             command=self.copy_translation)
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Text-to-speech button
        self.tts_btn = ttk.Button(output_btn_frame, text="🔊 Speak", 
                                 command=self.speak_translation)
        self.tts_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear output button
        clear_output_btn = ttk.Button(output_btn_frame, text="Clear", 
                                     command=self.clear_output)
        clear_output_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                       pady=(10, 0))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Bind events
        self.input_text.bind('<KeyRelease>', self.on_text_change)
        
    def populate_language_combos(self):
        """Populate language comboboxes"""
        # Add auto-detect option for source
        source_values = ['auto - Detect Language'] + [f"{code} - {name}" for code, name in self.language_list]
        self.source_combo['values'] = source_values
        self.source_combo.set('auto - Detect Language')
        
        # Target languages
        target_values = [f"{code} - {name}" for code, name in self.language_list]
        self.target_combo['values'] = target_values
        self.target_combo.set('en - English')
        
    def get_language_code(self, combo_value: str) -> str:
        """Extract language code from combo value"""
        return combo_value.split(' - ')[0]
        
    def swap_languages(self):
        """Swap source and target languages"""
        if self.source_lang.get() != 'auto':
            current_source = self.source_combo.get()
            current_target = self.target_combo.get()
            
            # Find the corresponding values
            source_code = self.get_language_code(current_source)
            target_code = self.get_language_code(current_target)
            
            # Swap
            self.target_combo.set(f"{source_code} - {self.languages[source_code].title()}")
            self.source_combo.set(f"{target_code} - {self.languages[target_code].title()}")
            
            # Also swap the text content
            input_text = self.input_text.get(1.0, tk.END).strip()
            output_text = self.output_text.get(1.0, tk.END).strip()
            
            if input_text and output_text and output_text != "Translation will appear here...":
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, output_text)
                self.clear_output()
                
    def on_text_change(self, event=None):
        """Handle text change in input area"""
        text = self.input_text.get(1.0, tk.END).strip()
        if text:
            self.status_var.set("Ready to translate")
        else:
            self.status_var.set("Ready")
            
    def clear_input(self):
        """Clear input text"""
        self.input_text.delete(1.0, tk.END)
        self.status_var.set("Ready")
        
    def clear_output(self):
        """Clear output text"""
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')
        
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, clipboard_text)
                self.status_var.set("Text pasted")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste text: {str(e)}")
            
    def copy_translation(self):
        """Copy translation to clipboard"""
        translation = self.output_text.get(1.0, tk.END).strip()
        if translation and translation != "Translation will appear here...":
            try:
                pyperclip.copy(translation)
                self.status_var.set("Translation copied to clipboard")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy text: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No translation to copy")
            
    def speak_translation(self):
        """Speak the translation using text-to-speech"""
        translation = self.output_text.get(1.0, tk.END).strip()
        if translation and translation != "Translation will appear here...":
            def speak():
                try:
                    self.tts_engine.say(translation)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", 
                                                                   f"Text-to-speech failed: {str(e)}"))
            
            # Run TTS in a separate thread to avoid blocking UI
            threading.Thread(target=speak, daemon=True).start()
            self.status_var.set("Speaking translation...")
        else:
            messagebox.showwarning("Warning", "No translation to speak")
            
    def translate_text(self):
        """Translate the input text"""
        text = self.input_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
            
        # Get language codes
        source_code = self.get_language_code(self.source_combo.get())
        target_code = self.get_language_code(self.target_combo.get())
        
        if source_code == target_code and source_code != 'auto':
            messagebox.showwarning("Warning", "Source and target languages cannot be the same")
            return
            
        # Disable translate button and show progress
        self.translate_btn.config(state='disabled')
        self.status_var.set("Translating...")
        
        # Run translation in a separate thread
        def translate_worker():
            try:
                # Perform translation
                if source_code == 'auto':
                    result = self.translator.translate(text, dest=target_code)
                    detected_lang = result.src
                    detected_name = self.languages.get(detected_lang, detected_lang).title()
                else:
                    result = self.translator.translate(text, src=source_code, dest=target_code)
                    detected_lang = source_code
                    detected_name = self.languages.get(detected_lang, detected_lang).title()
                
                # Update UI in main thread
                self.root.after(0, lambda: self.update_translation_result(
                    result.text, detected_name, detected_lang))
                    
            except Exception as e:
                self.root.after(0, lambda: self.handle_translation_error(str(e)))
                
        threading.Thread(target=translate_worker, daemon=True).start()
        
    def update_translation_result(self, translation: str, detected_lang_name: str, detected_lang_code: str):
        """Update the UI with translation result"""
        # Enable output text widget
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, translation)
        self.output_text.config(state='disabled')
        
        # Update status
        if self.get_language_code(self.source_combo.get()) == 'auto':
            self.status_var.set(f"Translated from {detected_lang_name}")
        else:
            self.status_var.set("Translation completed")
            
        # Re-enable translate button
        self.translate_btn.config(state='normal')
        
    def handle_translation_error(self, error_msg: str):
        """Handle translation errors"""
        self.status_var.set("Translation failed")
        self.translate_btn.config(state='normal')
        messagebox.showerror("Translation Error", 
                           f"Failed to translate text:\n{error_msg}\n\n"
                           "Please check your internet connection and try again.")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function to run the application"""
    try:
        app = LanguageTranslator()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()