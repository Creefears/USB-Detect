Set oShell = CreateObject("WScript.Shell")
strDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
oShell.Run "C:\Users\Shadow\AppData\Local\Programs\Python\Python313\pythonw.exe """ & strDir & "main.py""", 0, False
