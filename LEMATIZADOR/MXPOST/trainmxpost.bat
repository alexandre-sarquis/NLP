set project=%1%
set trdata=%2%

java -mx200m tagger.TrainTagger %project% %trdata%
java -mx100m maxent.GIS %project%/events %project%/tagfeatures.fmap %project%/model 100
