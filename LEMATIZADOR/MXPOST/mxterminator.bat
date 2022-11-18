@echo off

set CLASSPATH=%MXPOSTHOME%\mxpost.jar

java eos.TestEOS %1% <%2% >%3%

