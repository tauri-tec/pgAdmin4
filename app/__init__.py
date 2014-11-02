
# Get the GUI stuff
import wx

# We're going to be handling files and directories
import os

# Set up some button numbers for the menu

ID_ABOUT=101
ID_OPEN=102
ID_SAVE=103
ID_BUTTON1=300
ID_EXIT=200
ID_FRAME1LISTBOX1=150

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
        self.control = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE, size=wx.Size(500, 500))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu. filemenu is a local variable at this stage.
        filemenu= wx.Menu()
        # use ID_ for future easy reference - much better that "48", "404" etc
        # The & character indicates the short cut key
        filemenu.Append(ID_OPEN, "&Open"," Open a file to edit")
        filemenu.AppendSeparator()
        filemenu.Append(ID_SAVE, "&Save"," Save file")
        filemenu.AppendSeparator()
        filemenu.Append(ID_ABOUT, "&About"," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar) # Adding the MenuBar to the Frame content.
        # Note - previous line stores the whole of the menu into the current object

        # Define the code to be run when a menu option is selected
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_OPEN, self.OnOpen)
        wx.EVT_MENU(self, ID_SAVE, self.OnSave) # just "pass" in our demo

        # Set up a series of buttons arranged horizontally
        self.databases = wx.BoxSizer(wx.VERTICAL)
        self.buttons=[]
        # Note - give the buttons numbers 1 to 6, generating events 301 to 306
        # because IB_BUTTON1 is 300

        self.engine = sqlalchemy.create_engine(default_connection_string + 'postgres')
        self.connection = self.engine.connect()
        db_list = postgres_admin_queries.get_databases(self.connection)
        for db in db_list:
            i = db_list.index(db)
            self.buttons.append(wx.Button(self, ID_BUTTON1+i, db.dbname))
            # add that button to the sizer2 geometry
            self.databases.Add(self.buttons[i],1,wx.EXPAND)
            self.id_buttons[ID_BUTTON1+i] = db.dbname

            self.buttons[i].Bind(wx.EVT_BUTTON, self.onButton)

        self.table_listbox = wx.ListBox(choices=[], id=ID_FRAME1LISTBOX1,
            name='table_listbox', parent=self)
        self.table_listbox.Bind(wx.EVT_LISTBOX, self.onTableSelect,
            id=ID_FRAME1LISTBOX1)


        # Set up the overall frame verically - text edit window above buttons
        # We want to arrange the buttons vertically below the text edit window
        self.sizer=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.databases,0,wx.EXPAND)
        self.sizer.Add(self.table_listbox, 1, wx.EXPAND )
        self.sizer.Add(self.control, 2,wx.EXPAND)

        # Tell it which sizer is to be used for main frame
        # It may lay out automatically and be altered to fit window
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

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

    def onButton(self, e):
        dbname = self.id_buttons[e.GetId()]
        self.engine = sqlalchemy.create_engine(default_connection_string + dbname)


        #TODO: use the schema name too.
        inspector = sqlalchemy.inspect(self.engine)
        schema_names = inspector.get_schema_names()
        self.table_listbox.Set(self.engine.table_names())

        views = inspector.get_view_names()


    def onTableSelect(self, event):
        '''
        click list item and display the selected string in frame's title
        '''


        selName = self.table_listbox.GetStringSelection()
        self.SetTitle(selName)


        inspector = sqlalchemy.inspect(self.engine)
        print inspector.default_schema_name
        print inspector.get_columns(selName)
        print inspector.get_foreign_keys(selName)
        print inspector.get_indexes(selName)

        #TODO
        #if x is view:
            #print inspector.get_view_definition(selName)


        self.control.SetValue('')

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
            self.control.SetValue(filehandle.read())
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
            itcontains = self.control.GetValue()

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
