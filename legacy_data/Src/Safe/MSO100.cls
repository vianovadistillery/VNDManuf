VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "ThisOutlookSession"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
    Type RcdFmtSearch
        key As String * 5
        type  As String * 2
        company As String * 30
        compnum  As String * 5
        name As String * 20
        sPhone As String * 20
        sPhone1 As String * 20
        pstncc As String * 3
        email As String * 40
        www As String * 40
        'Personal details
        ContactFirstName(6) As String * 16
        ContactSurName(6) As String * 20
        ContactTitle(6) As String * 20
        ContactPhone(6) As String * 18 '+61 xxx3 9xxx xxxx
        contactmobile(6) As String * 18 '+61 x419 x338 x450
        ContactFax(6) As String * 18   '+61 x419 x338 x450
        Contactemail(6) As String * 40
        crlf As String * 1

        End Type
    Dim phonex As RcdFmtSearch



Sub main()
    Dim spObj As Object
    Dim MI As ContactItem
    Dim tmp As String
    
    Set spObj = CreateObject("Outlook.Application")
    
    Dim phonex As RcdFmtSearch

    Close #52
    Open "Z:\TPMANUF\phonex.who" For Random Shared As #52 Len = Len(phonex)
   

    rec% = 1
    Get #52, rec%, phonex

    Do While Not EOF(52) And rec% < 999 '???

        
        tmp$ = ""
        tmp$ = tmp$ & phonex.company$ & phonex.compnum
        
        tmp$ = tmp$ & phonex.email
        tmp$ = tmp$ & phonex.key & phonex.name
        tmp$ = tmp$ & phonex.pstncc & phonex.sPhone & phonex.sPhone1
        tmp$ = tmp$ & phonex.type & phonex.www
        tmp$ = tmp$ + vbCrLf
        
        For i = 1 To 6
        tmp$ = phonex.key
        tmp$ = tmp$ & "-->" & Str$(i)
        'tmp$ = tmp$ & Trim$(phonex.Contactemail(i))
        tmp$ = tmp$ & "F:" & phonex.ContactFax(i)
        'tmp$ = tmp$ & Trim$(phonex.ContactFirstName(i))
        tmp$ = tmp$ & "M:" & phonex.contactmobile(i) & "P:" & Trim$(phonex.ContactPhone(i))
        tmp$ = tmp$ & Trim$(phonex.ContactSurName(i)) & Trim$(phonex.ContactTitle(i))
        tmp$ = tmp$ & "<" & vbCrLf
        'MsgBox tmp$

        Next
        
        phone1$ = Trim$(phonex.pstncc) & Trim$(phonex.sPhone$)
        phone2$ = Trim$(phonex.sPhone1$)
        phone3$ = Trim$(phonex.contactmobile$(1))

        If Val(Mid$(phone1$, 1, 3)) <= 0 Then phone1$ = ""
        If Val(Mid$(phone1$, 1, 3)) = 111 Then phone1$ = ""
        If phone1$ > "" And Mid$(phone1$, 1, 1) = "0" Then
            phone1$ = "+61-" & Mid$(phone1$, 2)
        End If

        If Val(Mid$(phone2$, 1, 3)) <= 0 Then phone2$ = ""
        If Val(Mid$(phone2$, 1, 3)) = 111 Then phone2$ = ""
        If phone2$ > "" And Mid$(phone2$, 1, 1) = "0" Then
            phone2$ = "+61-" & Mid$(phone2$, 2)
        End If

        If Val(Mid$(phone3$, 1, 3)) <= 0 Then phone3$ = ""
        If Val(Mid$(phone3$, 1, 3)) = 111 Then phone3$ = ""
        If phone3$ > "" And Mid$(phone3$, 1, 1) = "0" Then
            phone3$ = "+61-" & Mid$(phone3$, 2)
        End If
        ok% = -1
        If phone1$ = "" And phone2$ = "" And phone3$ = "" Then ok% = 0

        If ok% Then

            For c% = 1 To 6
                If RTrim$(phonex.ContactFirstName(c%)) > "A" Then
                    If c% > 1 Then
                        phone1$ = phonex.ContactPhone$(c%)
                        phone2$ = phonex.ContactFax$(c%)
                        phone3$ = phonex.contactmobile$(c%)
                    End If

                    If Mid$(phone1$, 1, 1) <> "+" And Val(Mid$(phone1$, 1, 3)) <= 0 Then phone1$ = ""
                    If Val(Mid$(phone1$, 1, 3)) = 111 Then phone1$ = ""
                    If phone1$ > "" And Mid$(phone1$, 1, 1) = "0" Then
                        phone1$ = "+61-" & Mid$(phone1$, 2)
                    End If

                    If Mid$(phone2$, 1, 1) <> "+" And Val(Mid$(phone2$, 1, 3)) <= 0 Then phone2$ = ""
                    If Val(Mid$(phone2$, 1, 3)) = 111 Then phone2$ = ""
                    If phone2$ > "" And Mid$(phone2$, 1, 1) = "0" Then
                        phone2$ = "+61-" & Mid$(phone2$, 2)
                    End If

                    If Mid$(phone3$, 1, 1) <> "+" And Val(Mid$(phone3$, 1, 3)) <= 0 Then phone3$ = ""
                    If Val(Mid$(phone3$, 1, 3)) = 111 Then phone3$ = ""
                    If phone3$ > "" And Mid$(phone3$, 1, 1) = "0" Then
                        phone3$ = "+61-" & Mid$(phone3$, 2)
                    End If
                    
                    Set MI = spObj.CreateItem(olContactItem)
                    MI.LastName = RTrim$(phonex.ContactSurName(c%))
                    MI.FirstName = RTrim$(phonex.ContactFirstName(c%))
                    MI.BusinessTelephoneNumber = phone1$
                    MI.BusinessFaxNumber = phone2$
                    MI.MobileTelephoneNumber = phone3$
                    MI.CompanyName = phonex.company
                    MI.Body = phonex.key + phonex.type
                    MI.Email1Address = phonex.email
                    MI.WebPage = phonex.www
                    If Mid$(phonex.www, 1, 3) = "..." Then MI.WebPage = ""
                    '          MI.Display
                    If 1 = 1 Then
                        MI.Save
                    End If
                    'tmp = ""
                    'tmp = tmp & MI.LastName & "," & MI.FirstName & vbCrLf
                    'tmp = tmp & MI.BusinessTelephoneNumber & MI.MobileTelephoneNumber + vbCrLf
                    'tmp = tmp & MI.CompanyName + vbCrLf
                    'tmp = tmp & MI.Body + vbCrLf
                    'MsgBox tmp
                    Set MI = Nothing
                End If

            Next
            
        End If


    Get #52, , phonex: rec% = rec% + 1
    Loop

    Set spObj = Nothing


End Sub
