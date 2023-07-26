import openai
import gzip
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinterhtml import HtmlFrame
import io

# Set up your OpenAI API key
openai.api_key = 'apikey'

def process_file(file_path):
    try:
        # Check if the file is gzipped
        with open(file_path, 'rb') as f:
            magic_number = f.read(2)

        if magic_number == b'\x1f\x8b':
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                text = f.read()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        # Gzip the text if it's not already gzipped
        if magic_number != b'\x1f\x8b':
            compressed_text = gzip.compress(text.encode('utf-8'))
            text = gzip.decompress(compressed_text).decode('latin-1')

        # Split the text into sentences to preserve meaning
        sentences = text.split('. ')

        # Adjust chunking to ensure each chunk is within the token limit
        max_tokens = 4090  # Leave a buffer to avoid exceeding the limit
        chunks = []
        current_chunk = ''
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_tokens:
                current_chunk += sentence + '. '
            else:
                while len(current_chunk) > max_tokens:  # Split large chunks
                    chunks.append(current_chunk[:max_tokens])
                    current_chunk = current_chunk[max_tokens:]
                chunks.append(current_chunk)
                current_chunk = sentence + '. '
        if current_chunk:
            chunks.append(current_chunk)

        # Send each chunk to the model and collect the responses
        responses = []
        for i, chunk in enumerate(chunks):
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. The user message is a GZIP encoded datapackage."},
                    {"role": "user", "content": chunk}
                ],
                max_tokens=4000,  # Keep this value unchanged
                temperature=0.5,
                n=1,
            )
            # Colorize each chunk differently
            color = '#{:06x}'.format(i * 123456)  # Generate a color code
            responses.append((color, response['choices'][0]['message']['content'].strip()))

        return responses

    except Exception as e:
        return [('red', str(e))]

def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        results = process_file(file_path)
        show_result(results)

def show_result(results):
    root = tk.Tk()
    root.title('OpenAI ChatBot - Result')

    # Box for errors
    error_frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
    error_frame.pack(pady=5, padx=10, fill='x')
    error_label = tk.Label(error_frame, text='Errors:', font=('Helvetica', 12, 'bold'))
    error_label.pack(side=tk.LEFT)
    error_text = tk.Text(error_frame, wrap=tk.WORD, height=4, width=50)
    error_text.pack(side=tk.LEFT, padx=5, pady=5)
    copy_error_button = tk.Button(error_frame, text='Copy', command=lambda: copy_to_clipboard(error_text.get('1.0', tk.END).strip()))
    copy_error_button.pack(side=tk.RIGHT)

    # Box for model's text output
    model_frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
    model_frame.pack(pady=5, padx=10, fill='x')
    model_label = tk.Label(model_frame, text='Model Output:', font=('Helvetica', 12, 'bold'))
    model_label.pack(side=tk.LEFT)
    model_text = tk.Text(model_frame, wrap=tk.WORD, height=10, width=50)
    model_text.pack(side=tk.LEFT, padx=5, pady=5)
    copy_model_button = tk.Button(model_frame, text='Copy', command=lambda: copy_to_clipboard(model_text.get('1.0', tk.END).strip()))
    copy_model_button.pack(side=tk.RIGHT)

    for color, response in results:
        model_text.insert(tk.END, response + '\n', color)

    root.mainloop()

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo('Copy', 'Copied to clipboard.')

if __name__ == '__main__':
    root = tk.Tk()
    root.title('OpenAI ChatBot')

    label = tk.Label(root, text='Select a text file to process:')
    label.pack(pady=10)

    button = tk.Button(root, text='Open File', command=open_file)
    button.pack(pady=5)

    root.mainloop()
