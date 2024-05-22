import tkinter as tk
from tkinter import filedialog, Canvas, NW
import fitz

class SignatureApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Electronic Signature App")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Menu bar
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar)
        file_menu.add_command(label="Open PDF", command=self.open_pdf)
        file_menu.add_command(label="Save Signed PDF", command=self.save_signed_pdf)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

        # Drawing canvas
        self.canvas = Canvas(self, bg="white", width=600, height=200)
        self.canvas.pack(pady=20)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset_drawing)

        # Buttons
        button_frame = tk.Frame(self)
        clear_button = tk.Button(button_frame, text="Clear", command=self.clear_canvas)
        clear_button.pack(side=tk.LEFT, padx=10)
        apply_button = tk.Button(button_frame, text="Apply Signature", command=self.apply_signature)
        apply_button.pack(side=tk.LEFT, padx=10)
        button_frame.pack(pady=10)

        # PDF viewer
        self.pdf_viewer = Canvas(self, bg="gray", width=600, height=400)
        self.pdf_viewer.pack()

    def draw(self, event):
        x1, y1 = event.x, event.y
        x2, y2 = (event.x + 1), (event.y + 1)
        self.canvas.create_line(x1, y1, x2, y2, width=2, capstyle=tk.ROUND, smooth=True)

    def reset_drawing(self, event):
        self.canvas.bind("<B1-Motion>", self.draw)

    def clear_canvas(self):
        self.canvas.delete("all")

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_file = fitz.open(file_path)
            self.display_pdf(0)  # Display the first page by default

    def display_pdf(self, page_index):
        self.pdf_viewer.delete("all")
        page = self.pdf_file[page_index]  # Access the page using square brackets
        pix = page.getPixmap()
        pix_data = pix.getPNGData()
        image = tk.PhotoImage(data=pix_data)
        self.pdf_viewer.create_image(0, 0, anchor=NW, image=image)
        self.pdf_viewer.image = image  # Keep a reference to prevent garbage collection

    def apply_signature(self):
        if hasattr(self, "pdf_file"):
            signature_image = self.canvas.postscript(colormode="color")
            signature_image = fitz.Pixmap(signature_image, 0)

            for page_index in range(len(self.pdf_file)):
                page = self.pdf_file[page_index]  # Access the page using square brackets
                rect = fitz.Rect(50, 50, 250, 150)  # Position and size of the signature
                page.insertImage(rect, signature_image)

            self.display_pdf(0)  # Display the first page after applying the signature
        else:
            print("Please open a PDF file first.")

    def save_signed_pdf(self):
        if hasattr(self, "pdf_file"):
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if file_path:
                self.pdf_file.save(file_path)
        else:
            print("No PDF file has been opened or signed.")

if __name__ == "__main__":
    app = SignatureApp()
    app.mainloop()