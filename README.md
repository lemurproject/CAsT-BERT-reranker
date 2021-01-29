# CAsT-BERT-reranker

This project contains the python code to perform BERT reranking on a Solr index.  The components you will need to run this project are:
+ Solr
+ Lucindri (requires java)
+ Python 3.7+ 

## Setting Up Solr
###Zookeeper
1. Download apache zookeeper
1. Unzip zookeeper where it will run
1. Create zoo.cfg 
  1. Copy zoo_sample.cfg to zoo.cfg
  1. Update:
    1.dataDir=/bos/tmp0/cmw2/zookeeper
    1. clientPort=2181
    1. 4lw.commands.whitelist=*


## Indexing

## Running BERT
