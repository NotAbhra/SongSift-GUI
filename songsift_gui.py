import tkinter as tk
from tkinter import ttk, messagebox
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser

client_id = "your client ID"
client_secret = "your client secret ID"

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


class SongSiftApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SongSift")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f4f8')

        style = ttk.Style()
        style.configure("TLabel", font=("Akira Expanded", 28, "bold"), background='#f0f4f8', foreground="#333333")
        style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background='#009688', foreground="#ffffff")
        style.configure("Treeview", font=("Helvetica", 12), background='#ffffff', foreground="#333333", fieldbackground='#ffffff', rowheight=35)
        style.map('Treeview', background=[('selected', '#e0f7fa')])  

        self.center_frame = tk.Frame(root, bg='#f0f4f8')
        self.center_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.header_label = ttk.Label(self.center_frame, text="SongSift")
        self.header_label.pack(pady=20)

        self.instruction_label = ttk.Label(self.center_frame, text="Enter a song to get recommendations:", font=("Helvetica", 12))
        self.instruction_label.pack(pady=5)

        self.song_entry = tk.Entry(self.center_frame, width=50, font=("Helvetica", 14), bd=2, relief="solid", fg='#333333')
        self.song_entry.pack(pady=10)

    
        self.search_button = tk.Button(self.center_frame, text="Search", command=self.fetch_recommendations, font=("Helvetica", 16, "bold"), bg='#009688', fg='#ffffff', relief='flat', width=12, height=2, borderwidth=1)
        self.search_button.pack(pady=20)


        self.result_frame = tk.Frame(root, bg='#ffffff', bd=1, relief='solid')
        self.result_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.result_frame.configure(width=750, height=400)
        self.result_frame.place_forget()  # Initially hide the result frame

        self.result_tree = ttk.Treeview(self.result_frame, columns=("Track Name", "Artist"), show='headings', height=12)
        self.result_tree.heading("Track Name", text="Track Name")
        self.result_tree.heading("Artist", text="Artist")
        self.result_tree.column("Track Name", anchor=tk.W, width=450)
        self.result_tree.column("Artist", anchor=tk.W, width=300)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_tree.bind("<Double-1>", self.play_song)


        self.back_button = tk.Button(root, text="Back", command=self.go_back, font=("Helvetica", 16, "bold"), bg='#009688', fg='#ffffff', relief='flat', width=8, height=2, borderwidth=1)
        self.back_button.place(relx=0.95, rely=0.95, anchor=tk.SE, height=40, width=100)
        self.back_button.place_forget()

    def fetch_recommendations(self):
        songname = self.song_entry.get()
        self.result_tree.delete(*self.result_tree.get_children())

        recommendations = self.get_recommendations(songname)

        if recommendations:
            for track in recommendations:
                self.result_tree.insert("", tk.END, values=(track['name'], track['artists'][0]['name']), tags=(track['uri'],))
            self.show_result_frame()
        else:
            messagebox.showerror("Error", f"No recommendations found for '{songname}'")

    def get_recommendations(self, track_name):
        results = sp.search(q=track_name, type='track')
        if not results['tracks']['items']:
            return []

        track_uri = results['tracks']['items'][0]['uri']
        recommendations = sp.recommendations(seed_tracks=[track_uri])['tracks']
        return recommendations

    def play_song(self, event):
        item = self.result_tree.selection()[0]
        track_uri = self.result_tree.item(item, "tags")[0]
        track_url = f"https://open.spotify.com/track/{track_uri.split(':')[-1]}"
        webbrowser.open(track_url)

    def show_result_frame(self):
        self.result_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.result_frame.update_idletasks()
        self.back_button.place(relx=0.95, rely=0.95, anchor=tk.SE, height=40, width=100)
        self._animate_result_frame(self.result_frame.winfo_height(), 400)

    def _animate_result_frame(self, start_height, end_height, step=10, delay=10):
        def _animate():
            current_height = self.result_frame.winfo_height()
            if current_height < end_height:
                new_height = min(current_height + step, end_height)
                self.result_frame.configure(height=new_height)
                self.root.after(delay, _animate)
            else:
                self.result_frame.configure(height=end_height)  

        self.result_frame.configure(height=start_height)  
        _animate()

    def go_back(self):
        self.result_frame.place_forget()
        self.back_button.place_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = SongSiftApp(root)
    root.mainloop()
