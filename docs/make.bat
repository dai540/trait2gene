@ECHO OFF

set SPHINXBUILD=sphinx-build
set SOURCEDIR=source
set BUILDDIR=build

if "%1"=="" goto help

%SPHINXBUILD% -b %1 %SOURCEDIR% %BUILDDIR%\%1 %SPHINXOPTS%
goto end

:help
echo.
echo Please use `make.bat ^<builder^>` where ^<builder^> is one of
echo   html
echo.

:end

