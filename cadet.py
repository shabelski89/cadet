from tkinter import *
from tkinter.ttk import Treeview, Style
from database import Database
from tkinter import messagebox as mb


class InterFace:
    def __init__(self, main):
        self.root = main
        self._fields = {1: "Идентификатор", 2: "Фамилия", 3: "Имя", 4: "Отчество", 5: "Группа",
                        6: "Дата оценки", 7: "Оценка", 8: "Комментарий"}
        self._fields_db = {1: "c_id", 2: "snd_name", 3: "fst_name", 4: "f_name", 5: "groups",
                           6: "date", 7: "mark", 8: "desc"}
        self.initialize_user_interface()

    def initialize_user_interface(self):
        self.root.title("Журнал")
        self.root.config(bg='white')

        frames = {1: 'top', 2: 'bottom', 3: 'left', 4: 'right'}
        self.root.frames = {x: Frame() for x in frames.values()}
        for k, v in self.root.frames.items():
            v.pack(side=k, padx=10)

        self.root.labels = {x: Label(self.root.frames['left'],
                                     font=('arial', 20, 'bold'), text=x, padx=2, pady=2, bg='Ghost White')
                            for x in self._fields.values()}
        self.root.entrys = {x: Entry(self.root.frames['left'],
                                     font=('arial', 20, 'bold'), textvariable=StringVar(), width=20)
                            for x in self._fields.values()}

        for k, v in self._fields.items():
            self.root.labels[v].grid(row=k, column=0, stick=W)
            self.root.entrys[v].grid(row=k, column=1, stick=W)

        buttons = {'Добавить': self.insert_data, 'Удалить': self.delete_data, 'Обновить': self.update_data,
                   'Вывод': self.show_data, 'Очистить': self.clear_screen, 'Искать': self.search_data, 'Выйти': self.get_exit}

        self.root.buttons = {}
        for n, (k, v) in enumerate(buttons.items()):
            self.root.buttons[k] = Button(self.root.frames['bottom'], text=k, font=('arial', 20, 'bold'),
                                          width=10, height=1, bd=1, command=v)
            self.root.buttons[k].grid(row=0, column=n)

        self.root.style = Style(self.root)
        self.root.style.configure('Treeview', rowheight=36)

        self.root.tree = Treeview(self.root.frames['right'],
                                  height=len(self._fields), columns=tuple(self._fields.values()),
                                  selectmode=BROWSE, show='headings')

        for k, v in self._fields.items():
            self.root.tree.column(f'#{k}', minwidth=20, width=100, stretch=YES, anchor='c')
            self.root.tree.heading(f'#{k}', text=v)

        self.root.tree.grid(row=10, columnspan=len(self._fields), sticky='nsew')
        self.root.treeview = self.root.tree

    def clear_entry(self):
        for entry in self.root.entrys.values():
            entry.delete(0, END)

    def clear_screen(self, clear_entry=True):
        self.root.tree.delete(*self.root.tree.get_children())
        if clear_entry:
            self.clear_entry()

    def get_confirm(self, msg):
        ask = mb.askyesno(title='Предупреждение', message=msg)
        if ask:
            return True

    def get_exit(self):
        if self.get_confirm(msg="Вы уверены что хотите закрыть журнал?"):
            self.root.destroy()

    def insert_data(self):
        data = tuple(self.root.entrys[x].get() for x in self._fields.values())
        if "" in data:
            mb.showerror("Ошибка", "Должны быть заполнены все поля!")
        else:
            self.root.treeview.insert('', 'end', text='', values=data)
            with Database('cadet.sqlite') as db:
                db.execute('INSERT INTO cadet (c_id, snd_name, fst_name, f_name, groups, date, mark, desc) '
                           'VALUES (?, ?, ?, ?, ?, ?, ?, ?);', data)
            self.clear_entry()

    def delete_data(self):
        row_id = self.root.tree.focus()
        if row_id:
            c_id = self.root.tree.item(row_id)['values'][0]
            snd_name = self.root.tree.item(row_id)['values'][1]
            fst_name = self.root.tree.item(row_id)['values'][2]
            if self.get_confirm(msg=f"Вы уверены что хотите удалить запись - {c_id} {snd_name} {fst_name}?"):
                with Database('cadet.sqlite') as db:
                    db.execute('DELETE FROM cadet WHERE c_id=?;', (c_id,))
                self.root.treeview.delete(row_id)
                self.clear_entry()
        else:
            mb.showerror("Ошибка", "Выберите запись для удаления!")

    def update_data(self):
        row_id = self.root.tree.focus()
        c_id = self.root.tree.item(row_id)['values'][0]
        from_entry = {k: self.root.entrys[v].get() for k, v in self._fields.items() if self.root.entrys[v].get()}
        from_tree = self.root.tree.item(row_id)['values']

        tmp_dict = {i+1: from_tree[i] for i in range(len(from_tree)) if from_tree[i]}
        for i in from_entry:
            tmp_dict[i] = from_entry[i]
        update_tuple = (*tmp_dict.values(), c_id)
        with Database('cadet.sqlite') as db:
            db.execute('UPDATE cadet SET '
                       'c_id=?, snd_name=?, fst_name=?, f_name=?, groups=?, date=?, mark=?, desc=? WHERE c_id=?;',
                       update_tuple)
        self.show_data(c_id=c_id)

    def show_data(self, c_id=None):
        self.clear_screen()
        if c_id:
            with Database('cadet.sqlite') as db:
                cadets = db.query('SELECT * FROM cadet WHERE c_id=?;', (c_id,))
        else:
            with Database('cadet.sqlite') as db:
                cadets = db.query('SELECT * FROM cadet;')
        for c in cadets:
            self.root.treeview.insert('', 'end', text='', values=c)

    def search_data(self):
        self.clear_screen(clear_entry=False)
        from_entry = {k: self.root.entrys[v].get() for k, v in self._fields.items() if self.root.entrys[v].get()}
        if not from_entry:  # all([x > 0 for x in num1])
            mb.showerror("Ошибка", "Должно быть заполнено хотя бы одно поле!")
        else:
            tmp_dict = {self._fields_db[k]: v for k, v in from_entry.items()}
            cols = "=? AND ".join([self._fields_db[k] for k in from_entry]) + '=?'
            vals = tuple(v for v in tmp_dict.values())
            with Database('cadet.sqlite') as db:
                cadets = db.query(f'SELECT * FROM cadet WHERE {cols};', vals)
                for c in cadets:
                    self.root.treeview.insert('', 'end', text='', values=c)


if __name__ == '__main__':
    with Database('cadet.sqlite') as db:
        db.execute("CREATE TABLE IF NOT EXISTS cadet(c_id INTEGER PRIMARY KEY, snd_name text, fst_name text,  "
                   "f_name text, groups text, date text, mark int, desc text);")
    root = Tk()
    application = InterFace(root)
    application.root.mainloop()
