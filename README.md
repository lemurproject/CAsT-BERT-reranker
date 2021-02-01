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
+ Run zookeeper: 

### Solr
+ Download the latest version of Solr
+ Copy Solr to the server in a location where there is enough space for the CAsT index
+ Unzip Solr
+ Create a Solr Configuration
  + Copy _default configuration to [CONFIGURATION_NAME]
  + Makes this change to server/solr/configsets/CONFIG_NAME/solrconfig.xml
    + <statsCache class="org.apache.solr.search.stats.ExactStatsCache" />
  + Upload configuration: bin/solr zk upconfig -n [CONFIGUARATION_NAME] -z [ZK_HOST]:[ZK_PORT] -d server/solr/configsets/CONFIGURATION_NAME/conf/
+ Run Solr
  + cd [SOLR_DIRECTORY]
  + bin/solr -c -f -p 23232 -z [ZOOKEEPRER_HOST]:[ZOOKEEPER_PORT] -Denable.runtime.lib=true
+ Test solr is running by checking solr dashboard: [HOST]/solr/#/
+ Create a collection for CAR: http://[HOST]/solr/admin/collections?action=CREATE&name=[CAR_COLLECTION_NAME]&numShards=1&replicationFactor=1&collection.configName=[CONFIGURATION_NAME]&createNodeSet=[HOST]:[PORT]_solr
+ Create a collection for MARCO: http://[HOST]/solr/admin/collections?action=CREATE&name=[MARCO_COLLECTION_NAME]&numShards=1&replicationFactor=1&collection.configName=[CONFIGURATION_NAME]&createNodeSet=[HOST]:[PORT]_solr

## Indexing
+ Download Lucindri Indexer either from github (source code) or sourceforge (jar file)
+ Download CAR and MARCO data
+ Create indexing properties for CAR
+ Index CAR
+ Create indexing properties for MARCO
+ Index MARCO

## Running BERT
+ Install packages needed by search_gpu.py
+ Download model
+ Update search_gpu to point to correct model location, host, and collection names
+ Run on single gpu with at least 64G or RAM
