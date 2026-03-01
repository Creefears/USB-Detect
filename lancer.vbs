Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")

strDir = oFSO.GetParentFolderName(WScript.ScriptFullName) & "\"

' --- Try the compiled exe first ---
strExe = strDir & "dist\USB Detect.exe"
If oFSO.FileExists(strExe) Then
    oShell.Run """" & strExe & """", 0, False
    WScript.Quit
End If

' --- Fallback: run via Python ---
strScript = strDir & "main.py"

' Try pythonw from PATH
On Error Resume Next
oShell.Run "pythonw.exe """ & strScript & """", 0, False
If Err.Number = 0 Then WScript.Quit
Err.Clear

' Try common install locations
arrPaths = Array( _
    oShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python314\pythonw.exe", _
    oShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python313\pythonw.exe", _
    oShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python312\pythonw.exe", _
    oShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python311\pythonw.exe", _
    oShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python310\pythonw.exe", _
    "C:\Python314\pythonw.exe", _
    "C:\Python313\pythonw.exe", _
    "C:\Python312\pythonw.exe", _
    "C:\Python311\pythonw.exe", _
    "C:\Python310\pythonw.exe" _
)

For Each strPython In arrPaths
    If oFSO.FileExists(strPython) Then
        oShell.Run """" & strPython & """ """ & strScript & """", 0, False
        WScript.Quit
    End If
Next

On Error GoTo 0
MsgBox "Python introuvable. Installez Python ou utilisez le fichier .exe dans dist\.", vbExclamation, "USB Detect"
