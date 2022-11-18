echo off
set CLASSPATH=%MXPOSTHOME%\mxpost.jar
set PREPARADO=%1%
java -mx30m tagger.TestTagger %MXPOSTHOME%\port < %PREPARADO% > %PREPARADO%.tagged.txt
exit
