# CAsT-BERT-reranker

This project contains the python code to perform BERT reranking on a Solr index.  The components you will need to run this project are:
+ Solr
+ Lucindri (requires java)
+ Python 3.7+ 

## Setting Up Solr

### Zookeeper
+ Download apache zookeeper
+ Unzip zookeeper where it will run
+ Create zoo.cfg 
  + Copy zoo_sample.cfg to zoo.cfg
  + Update:
    + dataDir=/bos/tmp0/cmw2/zookeeper
    + clientPort=2181
    + 4lw.commands.whitelist=*
+ Run zookeeper: bin/zkServer.sh --config conf start-foreground

### Solr
+ Download the latest version of Solr
+ Copy Solr to the server in a location where there is enough space for the CAsT index
+ Unzip Solr
+ Create a Solr Configuration
  + Copy _default configuration to [CONFIG_NAME]
  + Makes this change to server/solr/configsets/CONFIG_NAME/solrconfig.xml
    + \<statsCache class="org.apache.solr.search.stats.ExactStatsCache" /\>
  + Upload configuration: bin/solr zk upconfig -n [CONFIG_NAME] -z [ZK_HOST]:[ZK_PORT] -d server/solr/configsets/CONFIG_NAME/conf/
+ Run Solr
  + cd [SOLR_DIRECTORY]
  + bin/solr -c -f -p 23232 -z [ZK_HOST]:[ZK_PORT] -Denable.runtime.lib=true
+ Test solr is running by checking solr dashboard: [SOLR_HOST]/solr/#/
+ Create a collection for CAR: http://[SOLR_HOST]/solr/admin/collections?action=CREATE&name=[CAR_COLLECTION_NAME]&numShards=1&replicationFactor=1&collection.configName=[CONFIG_NAME]&createNodeSet=[SOLR_HOST]:[SOLR_PORT]_solr
+ Create a collection for MARCO: http://[SOLR_HOST]/solr/admin/collections?action=CREATE&name=[MARCO_COLLECTION_NAME]&numShards=1&replicationFactor=1&collection.configName=[CONFIG_NAME]&createNodeSet=[SOLR_HOST]:[SOLR_PORT]_solr

## Indexing
+ Download Lucindri Indexer either from github or sourceforge
  + Sourceforge (executable jar file): https://sourceforge.net/projects/lemur/files/lemur/lucindri-1.2/
  + Github (source code): https://github.com/lemurproject/Lucindri
+ Download CAR and MARCO data
+ Create indexing properties for CAR
```
#implementation options
indexingPlatform=solr

# documentFormat options = text, wsj, gov2, json, wapo, warc, car, marco
documentFormat=car

#data options
dataDirectory=[CAR_DATA_FILE] #CAR file is a cbor file
indexDirectory=/ #Not needed for Solr index
indexName=[CAR_COLLECTION_NAME]

#field options
#If index.fulltext is set to true, a field with all document text is created
indexFullText=true
fieldNames=

#analyzer options
stemmer=kstem
removeStopwords=true
ignoreCase=true

#solr options
host=[ZK_HOST]
port=[ZK_PORT]
```
+ Index CAR: java -jar -Xmx16G LucindriIndexer-1.2-jar-with-dependencies.jar [CAR_PROPERTIES_FILENAME]
+ Create indexing properties for MARCO
```
#implementation options
indexingPlatform=solr

# documentFormat options = text, wsj, gov2, json, wapo, warc, car, marco
documentFormat=marco

#data options
dataDirectory=[MARCO_DATA_DIRECTORY] #MARCO should be a directory containing a tsv file
indexDirectory=/ #Not needed for Solr index
indexName=[MARCO_COLLECTION_NAME]

#field options
#If index.fulltext is set to true, a field with all document text is created
indexFullText=true
fieldNames=

#analyzer options
stemmer=kstem
removeStopwords=true
ignoreCase=true

#solr options
host=[ZK_HOST]
port=[ZK_PORT]
```
+ Index MARCO: java -jar -Xmx16G LucindriIndexer-1.2-jar-with-dependencies.jar [MARCO_PROPERTIES_FILENAME]

## Running BERT
We have provided a Flask web application for running queries on Solr and reranking with BERT.
+ Install packages needed by search_gpu.py
+ Download model: http://boston.lti.cs.cmu.edu/BERTFiles/bert_model.1600000.pkl
+ Update search_gpu.py to point to correct model location, solr host, and car and marco collection names (separated by commas)
+ Run on single gpu with at least 64G or RAM
+ Open CAsT search site on your GPU Host
