   ' M S C L S 0 1
	 open"msclass.msf" as #10 len=57
   field#10,25 as cldesc$,8 as clya$,8 as clyt$,8 as clyay$,8 as clyty$
   cls:color 4:locate 3,23:print "CLASS PROCESSING SET UP"
               locate 4,22:print"========================="
   key 1,"end"+chr$(13):key 2,"cls"+chr$(13)
80 locate 5,21:print chr$(26)
   color 7:locate 24,20:print"F1 - main menu.   F2 - Class procesing";
    color 2:locate 5,21
    print tab(20);"1.. Month end processing"
    print tab(20);"2.. Year end processing"
    print
    if f%=0 then 180
    if b%=1 then print"      M O N T H   E N D   P R O C E S S I N G   C O M P L E T E "
    if b%=2 then print"      Y E A R   E N D   P R O C E S S I N G   C O M P L E T E "
    f%=0
180 print:print tab(20);"Option..>";:input "",a$
    b$=" ":lset b$=a$:b%=val(b$)
    if a$="end" then close:bpgm$="msmenu":call exitpgm(bpgm$):chain bpgm$
    if a$="cls" then close:bpgm$="mscls03":call exitpgm(bpgm$):chain bpgm$
    if b%<1 or b%>2 then 80
    print
    x=15
    if b%=2 then 340
    '* Month prompt
    print tab(x);" This step clears all the monthly class information"
    print tab(x);"out of the master files. Once run there is no way to"
    print tab(x);"recover the information. Therefore is is recommended"
    print tab(x);"you run a final ranking report for the month before"
    print tab(x);"this step."
    e$="M O N T H L Y"
    goto 440
340 '* Yearly prompt
    color 14:print tab(x+5);"Y E A R   E N D   P R O C E S S I N G"
    color 2
    print tab(x);" This step clears all the monthly and the yearly"
    print tab(x);"class information out of the master files."
    print tab(x);"Once run there is no way to recover the information"
    print tab(x);"in that file.  Therefore it is recommended you run a"
    print tab(x);"final ranking report for the Year before this step."
    e$="Y E A R L Y"
    '* ASK to go on
440 print:print tab(x);"Do you wish to continue with ";e$;" processing?"
    print tab(x+14);:input "Enter (Y/N)..>",a$
    if a$="end" then close:bpgm$="msmenu":call exitpgm(bpgm$):chain bpgm$
    if a$="cls" then close:bpgm$="mscls03":call exitpgm(bpgm$):chain bpgm$
    if a$<>"y" and a$<>"Y" then 80
    '* Now clear the file
    for i%=1 to 99
    get#10,i%
    lset clya$=mkd$(0)
    lset clyt$=mkd$(0)
    if b%=2 then 570
    lset clyay$=mkd$(0)
    lset clyty$=mkd$(0)
570 put#10,i%
    next
    f%=1

