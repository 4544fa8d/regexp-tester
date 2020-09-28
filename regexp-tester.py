#!/usr/bin/env python3

import re
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


class Application(Gtk.Window):
    '''Główne okno aplikacji'''
    def __init__(self):
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)
        self.connect('destroy', self.__on_destroy)
        self.set_title('RegExp Tester')
        self.set_size_request(640, 480)
        vbox = Gtk.VBox()

        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        menu_bar = Gtk.MenuBar()
        file_menu_entry = Gtk.MenuItem('File')
        result_menu = Gtk.Menu()
        result_menu_save_to_file = Gtk.MenuItem('Save as...')
        result_menu_save_to_file.connect('activate', self.__on_result_menu_save_to_file)
        result_menu.append(result_menu_save_to_file)

        # quit menu item
        result_menu_quit = Gtk.MenuItem('Quit')
        result_menu_quit.connect('activate', self.__on_destroy)
        result_menu_quit.add_accelerator('activate', accel_group, Gdk.KEY_q, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)

        result_menu.append(result_menu_quit)
        file_menu_entry.set_submenu(result_menu)
        menu_bar.append(file_menu_entry)
        vbox.pack_start(menu_bar, False, False, 0)

        regExpLabel = Gtk.Label('Wprowadź wyrażenie regularne:')
        vbox.pack_start(regExpLabel, False, False, 0)

        self.__regExpEntry = Gtk.Entry()
        vbox.pack_start(self.__regExpEntry, False, False, 0)
        self.__regExpEntry.connect('activate', self.__onRegExpEntryChange)

        flags_label = Gtk.Label('Flagi wyrażenia:')
        vbox.pack_start(flags_label, False, False, 0)

        flags_table = Gtk.Table(2, 4, True)
        vbox.pack_start(flags_table, False, False, 0)

        self.__ascii_flag = Gtk.CheckButton('ASCII')
        flags_table.attach(self.__ascii_flag, 0, 1, 0, 1)
        self.__debug_flag = Gtk.CheckButton('DEBUG')
        flags_table.attach(self.__debug_flag, 1, 2, 0, 1)
        self.__ignorecase_flag = Gtk.CheckButton('IGNORECASE')
        flags_table.attach(self.__ignorecase_flag, 2, 3, 0, 1)
        self.__locale_flag = Gtk.CheckButton('LOCALE')
        flags_table.attach(self.__locale_flag, 3, 4, 0, 1)
        self.__multiline_flag = Gtk.CheckButton('MULTILINE')
        self.__multiline_flag.set_active(True)
        flags_table.attach(self.__multiline_flag, 0, 1, 1, 2)
        self.__dotall_flag = Gtk.CheckButton('DOTALL')
        self.__dotall_flag.set_active(True)
        flags_table.attach(self.__dotall_flag, 1, 2, 1, 2)
        self.__verbose_flag = Gtk.CheckButton('VERBOSE')
        flags_table.attach(self.__verbose_flag, 2, 3, 1, 2)

        textLabel = Gtk.Label('Wprowadź badany tekst:')
        vbox.pack_start(textLabel, False, False, 0)

        textViewScrollbar = Gtk.ScrolledWindow()
        self.__textView = Gtk.TextView()
        textViewScrollbar.add(self.__textView)
        vbox.pack_start(textViewScrollbar, True, True, 0)

        resultsLabel = Gtk.Label('Znalezione wyrażenia:')
        vbox.pack_start(resultsLabel, False, False, 0)

        resultListScrollbar = Gtk.ScrolledWindow()
        self.__list_store = Gtk.ListStore(str, int, int)
        self.__resultList = Gtk.TreeView(self.__list_store)
        textRenderer = Gtk.CellRendererText()
        textColumn = Gtk.TreeViewColumn(None, textRenderer)
        textColumn.add_attribute(textRenderer, 'text', 0)
        self.__resultList.append_column(textColumn)
        self.__resultList.connect('row-activated', self.__on_list_box_click)
        resultListScrollbar.add(self.__resultList)
        vbox.pack_start(resultListScrollbar, True, True, 0)

        self.add(vbox)
        self.show_all()

    def __on_result_menu_save_to_file(self, e):
        dlg = Gtk.FileChooserDialog('Saving result list', self, Gtk.FILE_CHOOSER_ACTION_SAVE, (Gtk.STOCK_CANCEL,Ggtk.RESPONSE_CANCEL, Gtk.STOCK_OK, Gtk.RESPONSE_OK))
        if dlg.run() == Gtk.RESPONSE_OK:
            filename = dlg.get_filename()
            f = open(filename, 'w')
            for row in self.__list_store:
                f.write('{0}\n'.format(row[0]))
            f.close()
        dlg.destroy()

    def __on_destroy(self, e=None):
        Gtk.main_quit()

    def __onRegExpEntryChange(self, e):
        #wyczyść listę wyników
        self.__list_store.clear()
        #pobierz wyrażenie regularne i tekst do przeszukania
        regExp = self.__regExpEntry.get_text()
        text_buffer = self.__textView.get_buffer()
        start_iter, end_iter = text_buffer.get_bounds()
        text = text_buffer.get_text(start_iter, end_iter, False)
        if regExp and text:
            #Ustal flagi wyrażenia
            flags = 0
            if self.__ascii_flag.get_active():
                flags |= re.ASCII
            if self.__debug_flag.get_active():
                flags |= re.DEBUG
            if self.__ignorecase_flag.get_active():
                flags |= re.IGNORECASE
            if self.__locale_flag.get_active():
                flags |= re.LOCALE
            if self.__multiline_flag.get_active():
                flags |= re.MULTILINE
            if self.__dotall_flag.get_active():
                flags |= re.DOTALL
            if self.__verbose_flag.get_active():
                flags |= re.VERBOSE
            #wyszukaj wszystkie wystąpienia wyrażenia w tekście
            for m in re.finditer(regExp, text, flags):
                s = m.group(0)
                self.__list_store.insert(-1, (s, m.start(), m.end()))

    def __on_list_box_click(self, tree_view, path, view_column):
        selection = tree_view.get_selection()
        tree_store, tree_iter = selection.get_selected()
        if tree_iter:
            start_offset = tree_store.get_value(tree_iter, 1)
            end_offset = tree_store.get_value(tree_iter, 2)
            text_buffer = self.__textView.get_buffer()
            start_iter = text_buffer.get_iter_at_offset(start_offset)
            end_iter = text_buffer.get_iter_at_offset(end_offset)
            text_buffer.select_range(start_iter, end_iter)
            self.__textView.scroll_to_iter(start_iter, 0.3)

    def run(self):
        Gtk.main()

app = Application()
app.run()
