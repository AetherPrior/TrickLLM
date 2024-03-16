#!/bin/bash
source /relevance-nfs/users/t-raoabhinav/opt/bin/activate; ray start --head;
for i in {1..3};
do
    ssh node-$i 'source /relevance-nfs/users/t-raoabhinav/opt/bin/activate; ray start --address='\''10.9.44.71:6379'\'';';
done

