@ECHO OFF
Z:
cd\tpmanuf
if exist msmisc.msf GOTO SIGNON
ECHO Can't Find System Files
GOTO ENDPGM
:SIGNON
path=%path%;Z:\qb7;Z:\tpmanuf;c:\tpexe;c:\winnt;c:\winnt\system32
SET LAST.PGM$='...................."
SET DB.OR.CR$=DB
SET TINTS.OR.A-F$=A - F
SET PARM$=......
SET PARM1$=......
SET PARM2$=......
SET PARM3$=......
SET SO=N
SET DOSTEMP=C:\DOS
@echo off

c:\TPEXE\SIGNON.EXE
:ENDPGM
