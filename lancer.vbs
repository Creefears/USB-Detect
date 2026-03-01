Set oShell = CreateObject("WScript.Shell")
strDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
oShell.Run "pythonw.exe """ & strDir & "main.py""", 0, False
