import queue
import re
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import textdistance

from src.Configuration import (
    Configuration,
    PARSER_DICT,
    MAGIC_SEARCH_PARSERS,
    EXTERNAL_SEARCH_PARSERS,
    SCRIPT_LINE,
)
from src.Parsers.SubsPleaseParser import SUBS_PLEASE_PARSER_NAME
from src.Parsers.NonMagicParserBase import NonMagicParserBase
from src.Show import Show
from src.ShowManager import ShowManager
from src.TorrentUtils import TorrentEngine

ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')

SEARCH_EVERYWHERE = 'Everywhere (magic search)'

NON_MAGIC_FILTER_HELP = (
    'Replace the parts of the filename that change between episodes with <<...>>:\n'
    '  <<anything>> - matches any text\n'
    '  <<fix:d:2>> - exactly 2 digits     <<fix:s:3>> - exactly 3 symbols\n'
    '  <<max:d:2>> - 1 to 2 digits        <<max0:d:2>> - 0 to 2 digits\n'
    'Example: [SubsPlease] Metallic Rouge - <<fix:d:2>> (1080p) [<<hex>>].mkv'
)


class LogWriter:
    '''stdout replacement that forwards prints from worker threads to the log panel'''
    def __init__(self, app) -> None:
        self.app = app

    def write(self, text):
        if text:
            self.app.post(lambda t=text: self.app.append_log(t))

    def flush(self):
        pass


class SparrowGUI:
    def __init__(self, root, config: Configuration) -> None:
        self.root = root
        self.config = config
        self.ui_queue = queue.Queue()
        self.busy = False

        self._build_window()
        self.refresh_show_list()

        self.root.after(100, self._poll_ui_queue)

    # ---------- thread plumbing ----------

    def post(self, fn):
        '''schedule fn to run on the UI thread'''
        self.ui_queue.put(fn)

    def _poll_ui_queue(self):
        while True:
            try:
                fn = self.ui_queue.get_nowait()
            except queue.Empty:
                break
            fn()

        self.root.after(100, self._poll_ui_queue)

    def run_async(self, fn, on_done, on_error):
        def worker():
            try:
                res = fn()
            except Exception as e:
                self.post(lambda err=e: on_error(err))
                return

            self.post(lambda r=res: on_done(r))

        threading.Thread(target=worker, daemon=True).start()

    # ---------- window ----------

    def _build_window(self):
        self.root.title('Sparrow')
        self.root.geometry('860x600')
        self.root.minsize(640, 420)

        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=8, pady=(8, 4))

        self.add_btn = ttk.Button(toolbar, text='Add show...', command=self.on_add_show)
        self.add_btn.pack(side='left')

        self.remove_btn = ttk.Button(toolbar, text='Remove selected', command=self.on_remove_show)
        self.remove_btn.pack(side='left', padx=(6, 0))

        self.update_btn = ttk.Button(toolbar, text='Update all', command=self.on_update_all)
        self.update_btn.pack(side='left', padx=(6, 0))

        self.status_var = tk.StringVar(value='')
        ttk.Label(toolbar, textvariable=self.status_var).pack(side='left', padx=(12, 0))

        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill='both', expand=True, padx=8, pady=4)

        self.tree = ttk.Treeview(tree_frame, columns=('title', 'source', 'last'), show='headings', selectmode='extended')
        self.tree.heading('title', text='Show')
        self.tree.heading('source', text='Source')
        self.tree.heading('last', text='Last episode you have')
        self.tree.column('title', width=280)
        self.tree.column('source', width=110, stretch=False)
        self.tree.column('last', width=380)

        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='both', expand=True)

        log_frame = ttk.LabelFrame(self.root, text='Log')
        log_frame.pack(fill='both', padx=8, pady=(4, 8))

        self.log_text = tk.Text(log_frame, height=9, state='disabled', wrap='word')
        log_scroll = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side='right', fill='y')
        self.log_text.pack(side='left', fill='both', expand=True)

    def set_busy(self, busy, status=''):
        self.busy = busy
        state = 'disabled' if busy else 'normal'
        for btn in (self.add_btn, self.remove_btn, self.update_btn):
            btn.configure(state=state)
        self.status_var.set(status)

    def append_log(self, text):
        text = ANSI_PATTERN.sub('', text)
        self.log_text.configure(state='normal')
        self.log_text.insert('end', text)
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def show_error(self, err):
        messagebox.showerror('Sparrow', f'Something went wrong:\n{err}', parent=self.root)

    def refresh_show_list(self):
        self.tree.delete(*self.tree.get_children())
        for show in self.config.show_list:
            last = show.last_episode if show.last_episode is not None else '<nothing yet - everything will be downloaded>'
            self.tree.insert('', 'end', values=(show.title, show.parser_name, last))

    # ---------- actions ----------

    def on_add_show(self):
        AddShowWizard(self)

    def on_remove_show(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo('Sparrow', 'Select the show(s) you want to remove first', parent=self.root)
            return

        children = list(self.tree.get_children())
        to_remove = [self.config.show_list[children.index(item)] for item in selection]

        titles = '\n'.join(f' - {show.title}' for show in to_remove)
        if not messagebox.askyesno('Sparrow', f'Remove these shows from tracking?\n\n{titles}', parent=self.root):
            return

        for show in to_remove:
            self.config.remove_show(show)
            self.append_log(f'Removed: "{show.title}"\n')

        self.config.update_config()
        self.refresh_show_list()

    def on_update_all(self):
        self.set_busy(True, 'Checking for updates...')
        self.append_log('\n=== Checking for updates ===\n')

        config = self.config

        def work():
            original_stdout = sys.stdout
            sys.stdout = LogWriter(self)
            try:
                updates, new_config = ShowManager(config).check_for_updates()

                if len(updates) > 0:
                    engine = TorrentEngine(config[SCRIPT_LINE])
                    for magnet in updates:
                        engine.add_download(magnet)
                    engine.download()

                return updates, new_config
            finally:
                sys.stdout = original_stdout

        def done(res):
            updates, new_config = res
            self.set_busy(False)

            if len(updates) == 0:
                self.append_log('Everything seems to be up to date\n')
                return

            keep = messagebox.askyesno(
                'Sparrow',
                f'Started {len(updates)} download(s) in your torrent client.\n\n'
                'Did they all start correctly?\n\n'
                'Yes - remember the progress\n'
                'No - keep the old state so you can retry later',
                parent=self.root,
            )

            if keep:
                self.config = new_config
                self.config.update_config()
                self.refresh_show_list()
                self.append_log('Progress saved\n')
            else:
                self.append_log('Progress NOT saved, run "Update all" again to retry\n')

        def error(err):
            self.set_busy(False)
            self.append_log(f'Update failed: {err}\n')
            self.show_error(err)

        self.run_async(work, done, error)


class AddShowWizard(tk.Toplevel):
    def __init__(self, app: SparrowGUI) -> None:
        super().__init__(app.root)
        self.app = app

        self.title('Add show')
        self.geometry('720x560')
        self.transient(app.root)
        self.grab_set()

        self.parser = None
        self.parser_name = None
        self.show_title = None
        self.show_link = None
        self.episodes = []
        self.filter_value = None
        self.filtered_episodes = []
        self.search_results = []

        self.container = ttk.Frame(self)
        self.container.pack(fill='both', expand=True, padx=10, pady=10)

        self._build_search_frame()

    def _clear(self):
        for child in self.container.winfo_children():
            child.destroy()

    def _error(self, err):
        messagebox.showerror('Sparrow', str(err), parent=self)

    def _episode_label(self, episode):
        if len(episode) > 2:
            return f'{episode[0]}    [{episode[2]}]'
        return str(episode[0])

    # ---------- step 1: search ----------

    def _build_search_frame(self):
        self._clear()

        frame = self.container

        ttk.Label(frame, text='Show name:').grid(row=0, column=0, sticky='w')

        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(frame, textvariable=self.query_var)
        query_entry.grid(row=0, column=1, sticky='ew', padx=6)
        query_entry.focus_set()

        ttk.Label(frame, text='Look on:').grid(row=1, column=0, sticky='w', pady=(6, 0))

        self.source_var = tk.StringVar(value=SEARCH_EVERYWHERE)
        sources = [SEARCH_EVERYWHERE] + MAGIC_SEARCH_PARSERS + EXTERNAL_SEARCH_PARSERS
        source_box = ttk.Combobox(frame, textvariable=self.source_var, values=sources, state='readonly')
        source_box.grid(row=1, column=1, sticky='ew', padx=6, pady=(6, 0))

        self.search_btn = ttk.Button(frame, text='Search', command=self._on_search)
        self.search_btn.grid(row=0, column=2, rowspan=2, sticky='ns')

        self.search_status = ttk.Label(frame, text='')
        self.search_status.grid(row=2, column=0, columnspan=3, sticky='w', pady=(6, 0))

        self.results_list = tk.Listbox(frame)
        self.results_list.grid(row=3, column=0, columnspan=3, sticky='nsew', pady=6)

        self.next_btn = ttk.Button(frame, text='Next >', command=self._on_search_next, state='disabled')
        self.next_btn.grid(row=4, column=2, sticky='e')

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

        query_entry.bind('<Return>', lambda _: self._on_search())

    def _on_search(self):
        query = self.query_var.get().strip()
        if query == '':
            self._error('Enter a show name first')
            return

        source = self.source_var.get()

        self.search_btn.configure(state='disabled')
        self.next_btn.configure(state='disabled')
        self.search_status.configure(text='Searching... (this can take a while)')

        def work():
            results = []

            if source in EXTERNAL_SEARCH_PARSERS:
                # these sites can't list their shows, we go straight to their search page
                link = PARSER_DICT[source]().process_query(query)
                return [(source, query, link)]

            targets = MAGIC_SEARCH_PARSERS if source == SEARCH_EVERYWHERE else [source]

            for parser_name in targets:
                for title, link in PARSER_DICT[parser_name]().get_all_shows(query):
                    distance = textdistance.levenshtein(title.lower(), query.lower())
                    results.append((parser_name, title, link, distance))

            results.sort(key=lambda r: r[3])
            return [(name, title, link) for name, title, link, _ in results[:25]]

        def done(results):
            self.search_btn.configure(state='normal')
            self.search_status.configure(text='')
            self.search_results = results
            self.results_list.delete(0, 'end')

            if len(results) == 0:
                self.search_status.configure(text="Search didn't return any results")
                return

            for parser_name, title, _ in results:
                self.results_list.insert('end', f'{title}    -    {parser_name}')

            self.results_list.selection_set(0)
            self.next_btn.configure(state='normal')

        def error(err):
            self.search_btn.configure(state='normal')
            self.search_status.configure(text='')
            self._error(err)

        self.app.run_async(work, done, error)

    def _on_search_next(self):
        selection = self.results_list.curselection()
        if not selection:
            return

        self.parser_name, self.show_title, self.show_link = self.search_results[selection[0]]
        self.parser = PARSER_DICT[self.parser_name]()

        self.search_status.configure(text='Loading episode list...')
        self.next_btn.configure(state='disabled')
        self.search_btn.configure(state='disabled')

        def work():
            probe = Show(self.show_title, '', '', self.show_link, '')
            return self.parser.get_all_show_episodes(probe, 200)

        def done(episodes):
            if len(episodes) == 0:
                self.search_status.configure(text='')
                self.search_btn.configure(state='normal')
                self.next_btn.configure(state='normal')
                self._error(f'"{self.show_title}" doesn\'t have any episodes at the moment, try again later')
                return

            self.episodes = episodes

            if self.parser_name == SUBS_PLEASE_PARSER_NAME:
                self._build_quality_frame()
            else:
                self._build_filter_frame()

        def error(err):
            self.search_status.configure(text='')
            self.search_btn.configure(state='normal')
            self.next_btn.configure(state='normal')
            self._error(err)

        self.app.run_async(work, done, error)

    # ---------- step 2a: quality (SubsPlease) ----------

    def _build_quality_frame(self):
        self._clear()

        frame = self.container

        ttk.Label(frame, text=f'Choose quality for "{self.show_title}":').pack(anchor='w')

        self.quality_var = tk.StringVar(value='1080')
        for quality in ('1080', '720', '480'):
            ttk.Radiobutton(frame, text=f'{quality}p', variable=self.quality_var, value=quality).pack(anchor='w', pady=2)

        ttk.Button(frame, text='Next >', command=self._on_quality_next).pack(anchor='e', pady=(12, 0))

    def _on_quality_next(self):
        self.filter_value = self.quality_var.get()
        filtered = self.parser.apply_filter(self.parser.process_user_filter(self.filter_value), self.episodes)

        if len(filtered) == 0:
            self._error(f'No episodes available in {self.filter_value}p, pick another quality')
            return

        self.filtered_episodes = filtered
        self._build_last_episode_frame()

    # ---------- step 2b: filter (EZTV / non-magic sites) ----------

    def _build_filter_frame(self):
        self._clear()

        frame = self.container
        editable = isinstance(self.parser, NonMagicParserBase)

        ttk.Label(frame, text='Pick an episode to build the filter from:').grid(row=0, column=0, columnspan=2, sticky='w')

        self.episode_list = tk.Listbox(frame)
        self.episode_list.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=6)

        for episode in self.episodes:
            self.episode_list.insert('end', self._episode_label(episode))

        help_text = NON_MAGIC_FILTER_HELP if editable else 'The episode number is detected automatically (SxxExx)'
        ttk.Label(frame, text=help_text, justify='left').grid(row=2, column=0, columnspan=2, sticky='w')

        ttk.Label(frame, text='Filter:').grid(row=3, column=0, sticky='w', pady=(6, 0))

        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(frame, textvariable=self.filter_var, state='normal' if editable else 'readonly')
        filter_entry.grid(row=3, column=1, sticky='ew', padx=(6, 0), pady=(6, 0))

        preview_bar = ttk.Frame(frame)
        preview_bar.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(6, 0))

        ttk.Button(preview_bar, text='Preview matches', command=self._on_preview_filter).pack(side='left')
        self.preview_status = ttk.Label(preview_bar, text='')
        self.preview_status.pack(side='left', padx=(8, 0))

        self.preview_list = tk.Listbox(frame, height=6)
        self.preview_list.grid(row=5, column=0, columnspan=2, sticky='nsew', pady=6)

        ttk.Button(frame, text='Next >', command=self._on_filter_next).grid(row=6, column=1, sticky='e')

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=2)
        frame.rowconfigure(5, weight=1)

        self.episode_list.bind('<<ListboxSelect>>', self._on_episode_pick)

        self.episode_list.selection_set(0)
        self._on_episode_pick(None)

    def _on_episode_pick(self, _event):
        selection = self.episode_list.curselection()
        if not selection:
            return

        title = str(self.episodes[selection[0]][0])

        if isinstance(self.parser, NonMagicParserBase):
            self.filter_var.set(title)
        else:
            self.filter_var.set(self.parser.get_filter(title))

    def _apply_current_filter(self):
        return self.parser.apply_filter(self.parser.process_user_filter(self.filter_var.get()), self.episodes)

    def _on_preview_filter(self):
        filtered = self._apply_current_filter()

        self.preview_list.delete(0, 'end')
        for episode in filtered:
            self.preview_list.insert('end', self._episode_label(episode))

        self.preview_status.configure(text=f'{len(filtered)} episode(s) match')

    def _on_filter_next(self):
        if self.filter_var.get().strip() == '':
            self._error('Pick an episode first')
            return

        filtered = self._apply_current_filter()

        if len(filtered) == 0:
            self._error("The filter doesn't match any episodes, adjust it and use \"Preview matches\"")
            return

        self.filter_value = self.filter_var.get()
        self.filtered_episodes = filtered
        self._build_last_episode_frame()

    # ---------- step 3: last episode ----------

    def _build_last_episode_frame(self):
        self._clear()

        frame = self.container

        ttk.Label(
            frame,
            text='Select the last episode you already have.\nEverything newer will be downloaded on the next "Update all".',
            justify='left',
        ).pack(anchor='w')

        self.last_list = tk.Listbox(frame)
        self.last_list.pack(fill='both', expand=True, pady=6)

        self.last_list.insert('end', '<I have none of these - download everything>')
        for episode in self.filtered_episodes:
            self.last_list.insert('end', self._episode_label(episode))

        # default to the newest episode so nothing gets downloaded by accident
        self.last_list.selection_set(1 if len(self.filtered_episodes) > 0 else 0)

        ttk.Button(frame, text='Add show', command=self._on_add).pack(anchor='e')

    def _on_add(self):
        selection = self.last_list.curselection()
        if not selection:
            return

        last_episode = None
        if selection[0] > 0:
            last_episode = self.filtered_episodes[selection[0] - 1][0]

        show = Show(self.show_title, self.parser_name, self.filter_value, self.show_link, last_episode)

        if show in self.app.config.show_list:
            self._error('This show is already in your list')
            return

        self.app.config.add_show(show)
        self.app.config.update_config()
        self.app.refresh_show_list()
        self.app.append_log(f'Added: "{show.title}" ({show.parser_name})\n')

        self.destroy()


def run_gui():
    root = tk.Tk()
    root.withdraw()

    config = Configuration.try_parse_config()

    if config is None:
        messagebox.showinfo(
            'Sparrow',
            "I couldn't find a config file, so let's get you started.\n\n"
            'Choose the folder where new episodes should go.',
        )
        download_dir = filedialog.askdirectory(title='Where should new episodes go?')

        if not download_dir:
            return

        config = Configuration.create_config(download_dir)

    root.deiconify()
    SparrowGUI(root, config)
    root.mainloop()
