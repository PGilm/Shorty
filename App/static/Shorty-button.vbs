OPTION Explicit

Public param
param = "(No%20parameter%20passed)"
if WScript.Arguments.Count > 0 then param = WScript.Arguments(0)
param = Replace(param, "%20", " ")

Dim objFSO
Set objFSO = CreateObject("Scripting.FileSystemObject")
Dim objSCR
Set objSCR = CreateObject("WScript.Shell")
If objFSO.FileExists(".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param & " AutoPressPG "," AutoPressPG ")-1) _
			& ".ahk") = true Then
'    Msgbox ".\AutoPressPG\AutoPressPG-" _
'		& Left(param,instr(param," AutoPressPG ")-1) & ".ahk Exists!"
	objSCR.Run (""".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param," AutoPressPG ")-1) & ".ahk""")
ElseIf objFSO.FileExists(".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param & " AutoPressPG "," AutoPressPG ")-1) _
			& ".lnk") = true Then
'    Msgbox ".\AutoPressPG\AutoPressPG-" _
'		& Left(param,instr(param," AutoPressPG ")-1) & ".lnk Exists!"
	objSCR.Run (""".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param," AutoPressPG ")-1) & ".lnk""")
ElseIf objFSO.FileExists(".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param & " AutoPressPG "," AutoPressPG ")-1) _
			& ".vbs") = true Then
'    Msgbox ".\AutoPressPG\AutoPressPG-" _
'		& Left(param,instr(param," AutoPressPG ")-1) & ".vbs Exists!"
	objSCR.Run (""".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param," AutoPressPG ")-1) & ".vbs""")
ElseIf objFSO.FileExists(".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param & " AutoPressPG "," AutoPressPG ")-1) _
			& ".js") = true Then
'    Msgbox ".\AutoPressPG\AutoPressPG-" _
'		& Left(param,instr(param," AutoPressPG ")-1) & ".js Exists!"
	objSCR.Run (""".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param," AutoPressPG ")-1) & ".js""")
ElseIf objFSO.FileExists(".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param & " AutoPressPG "," AutoPressPG ")-1) _
			& ".exe") = true Then
'    Msgbox ".\AutoPressPG\AutoPressPG-" _
'		& Left(param,instr(param," AutoPressPG ")-1) & ".exe Exists!"
	objSCR.Run (""".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param," AutoPressPG ")-1) & ".exe""")
Else
	Msgbox ".\AutoPressPG\AutoPressPG-" _
		& Left(param,instr(param & " AutoPressPG "," AutoPressPG ")-1) _
			& ".ahk .lnk .vbs .js .exe Don't Exist!" & vbcrlf & vbcrlf _
				& "This external vbs process with" & vbcrlf & vbcrlf _
					& """" & param & """" & vbcrlf & vbcrlf _
						& "as the passed parameter(s)"
End If
Set objFSO = Nothing
Set objSCR = Nothing
