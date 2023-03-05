To import the QTA Notepad++ User Defined Langauge:
==================================================
	On the top bar (with "File" Edit" etc.), click "Language" -> "User Defined Language" -> "Define your language..."
	Then click "Import..." then find and select the "QTX Assembly.xml" file.



To get access to an instant assemble button in Notepad++:
=========================================================
	On the top bar, click "Plugins" -> "Plugins Admin"
	Install plugins: NppExec, Customize Toolbar

	Now press F6, and paste this into the box (replace PROJECT_PATH with your correct path to the project):

set PROJECT_PATH = C:\Users\Devin\Desktop\QT
npp_save
py "$(PROJECT_PATH)\QT Assembler\QTA.py" "$(FULL_CURRENT_PATH)"

	Then hit "Save" and name it something like "QT Assemble Script"
	Now go into "Plugins" -> "NppExec" -> "Advanced Options"
	At the bottom left, in the "Menu Item" box:
		Give the shortcut a name like "QT Assemble"
		The associated script will be the "QT Assemble Script" from before (or whatever name you chose)
	
	Now, go to %APPDATA%\Notepad++\plugins\Config\CustomizeToolbar.btn
	Paste in the following:

Macro,QT Assemble,,,*#FF00C9,*#FF00C9:QT

	Replace "QT Assemble" with whatever name you chose for the shortcut