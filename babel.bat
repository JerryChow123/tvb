@echo off

:choice
set /P c=Are you compile only? [Y/N]
if /I "%c%" EQU "Y" goto :compile
if /I "%c%" EQU "N" goto :all
goto :choice

:all
pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel update -i messages.pot -d app/translations
goto compile
:compile
pybabel compile -d app/translations