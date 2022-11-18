rem @echo off

set CLASSPATH=%MXPOSTHOME%\mxpost.jar

java -mx30m tagger.TestTagger %1% 
