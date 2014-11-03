
# Get the GUI stuff
import wx

# We're going to be handling files and directories
import os

# Set up some button numbers for the menu

ID_DB_LISTBOX=300
ID_TABLE_LISTBOX=150
ID_RUN_BUTTON=400


import sqlalchemy

import postgres_admin_queries

default_connection_string = 'postgres://localhost:5432/'

class MainWindow(wx.Frame):
    id_buttons = {}

    engine = None
    connection = None

    def __init__(self,parent,title):
        # based on a frame, so set up the frame
        wx.Frame.__init__(self,parent,wx.ID_ANY, title)

        # Add a text editor and a status bar
        # Each of these is within the current instance
        # so that we can refer to them later.
        self.editor = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE, size=wx.Size(500, 500))
        self.results = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE, size=wx.Size(500, 200))

        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu. filemenu is a local variable at this stage.
        filemenu= wx.Menu()
        # use ID_ for future easy reference - much better that "48", "404" etc
        # The & character indicates the short cut key
        filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_SAVE, "&Save"," Save file")
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar) # Adding the MenuBar to the Frame content.
        # Note - previous line stores the whole of the menu into the current object

        # Define the code to be run when a menu option is selected
        wx.EVT_MENU(self, wx.ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnOpen)
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnSave) # just "pass" in our demo


        self.engine = sqlalchemy.create_engine(default_connection_string + 'postgres')
        self.connection = self.engine.connect()
        db_list = postgres_admin_queries.get_databases(self.connection)

        self.db_listbox = wx.ListBox(choices=[], id=ID_DB_LISTBOX,
            name='table_listbox', parent=self)
        self.db_listbox.Bind(wx.EVT_LISTBOX, self.onDBSelect,
            id=ID_DB_LISTBOX)
        self.db_listbox.Set([db.dbname for db in db_list])

        self.table_listbox = wx.ListBox(choices=[], id=ID_TABLE_LISTBOX,
            name='table_listbox', parent=self)
        self.table_listbox.Bind(wx.EVT_LISTBOX, self.onTableSelect,
            id=ID_TABLE_LISTBOX)


        self.inner_panel=wx.BoxSizer(wx.VERTICAL)
        self.inner_panel.Add(self.editor, 0, wx.EXPAND)
        self.inner_panel.Add(self.results, 0, wx.EXPAND)

        # Set up the overall frame verically - text edit window above buttons
        # We want to arrange the buttons vertically below the text edit window
        self.sizer=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.db_listbox,0,wx.EXPAND)
        self.sizer.Add(self.table_listbox, 1, wx.EXPAND )
        self.sizer.Add(self.inner_panel, 2, wx.EXPAND)

        # Set up a series of buttons arranged vertically over the top
        self.outer_panel = wx.BoxSizer(wx.VERTICAL)

        #Menu buttons
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        run = wx.Button(self, ID_RUN_BUTTON, 'Run')
        self.buttons.Add(run)
        run.Bind(wx.EVT_BUTTON, self.onRun)

        self.outer_panel.Add(self.buttons, 0, wx.EXPAND)
        self.outer_panel.Add(self.sizer, 1, wx.EXPAND)

        # Tell it which sizer is to be used for main frame
        # It may lay out automatically and be altered to fit window
        self.SetSizer(self.outer_panel)
        self.SetAutoLayout(1)
        self.outer_panel.Fit(self)

        # Show it !!!
        self.Show(1)

        # Define widgets early even if they're not going to be seen
        # so that they can come up FAST when someone clicks for them!
        self.aboutme = wx.MessageDialog( self, " pgAdmin4 \n"
                            " in wxPython & SQLAlchemy.\n\n Created by Tauri-Tec Ltd. \n\nhttp://www.tauri-tec.com","About pgAdmin4", wx.OK)
        self.doiexit = wx.MessageDialog( self, " Exit - R U Sure? \n",
                        "GOING away ...", wx.YES_NO)

        # dirname is an APPLICATION variable that we're choosing to store
        # in with the frame - it's the parent directory for any file we
        # choose to edit in this frame
        self.dirname = ''

    def onDBSelect(self, e):
        dbname = self.db_listbox.GetStringSelection()
        self.engine = sqlalchemy.create_engine(default_connection_string + dbname)
        self.connection = self.engine.connect()
        self.SetTitle('Connected to %s' % dbname)

        #TODO: use the schema name too.
        inspector = sqlalchemy.inspect(self.engine)
        schema_names = inspector.get_schema_names()
        self.table_listbox.Set(self.engine.table_names())

        views = inspector.get_view_names()
        for v in views:
            self.table_listbox.Append(v)

    def onTableSelect(self, event):
        '''
        click list item and display the selected string in frame's title
        '''


        selName = self.table_listbox.GetStringSelection()

        inspector = sqlalchemy.inspect(self.engine)
        print inspector.default_schema_name
        print inspector.get_columns(selName)
        print inspector.get_foreign_keys(selName)
        print inspector.get_indexes(selName)

        #TODO
        #if x is view:
            #print inspector.get_view_definition(selName)

        self.editor.SetValue('')

    def onRun(self, event):
        sql = self.editor.GetValue()
        try:
            results = self.connection.execute(sql).fetchall()
        except Exception, e:
            results = e.message
        self.results.SetValue(str(results))

    def OnAbout(self,e):
        # A modal show will lock out the other windows until it has
        # been dealt with. Very useful in some programming tasks to
        # ensure that things happen in an order that the programmer
        # expects, but can be very frustrating to the user if it is
        # used to excess!
        self.aboutme.ShowModal() # Shows it
        # widget / frame defined earlier so it can come up fast when needed

    def OnExit(self,e):
        # A modal with an "are you sure" check - we don't want to exit
        # unless the user confirms the selection in this case ;-)
        igot = self.doiexit.ShowModal() # Shows it
        if igot == wx.ID_YES:
            self.Close(True) # Closes out this simple application

    def OnOpen(self,e):
        # In this case, the dialog is created within the method because
        # the directory name, etc, may be changed during the running of the
        # application. In theory, you could create one earlier, store it in
        # your frame object and change it when it was called to reflect
        # current parameters / values
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()

            # Open the file, read the contents and set them into
            # the text edit window
            filehandle=open(os.path.join(self.dirname, self.filename),'r')
            self.editor.SetValue(filehandle.read())
            filehandle.close()

            # Report on name of latest file read
            self.SetTitle("Editing ... "+self.filename)
            # Later - could be enhanced to include a "changed" flag whenever
            # the text is actually changed, could also be altered on "save" ...
        dlg.Destroy()

    def OnSave(self,e):
        # Save away the edited text
        # Open the file, do an RU sure check for an overwrite!
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", \
                wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            # Grab the content to be saved
            itcontains = self.editor.GetValue()

            # Open the file for write, write, close
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            filehandle=open(os.path.join(self.dirname, self.filename),'w')
            filehandle.write(itcontains)
            filehandle.close()
        # Get rid of the dialog to keep things tidy
        dlg.Destroy()

# Set up a window based app, and create a main window in it
app = wx.App(False)
view = MainWindow(None, "pgAdmin4")
# Enter event loop
app.MainLoop()
