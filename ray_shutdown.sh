#!/bin/bash
for i in {0..3};
do
    ssh node-$i 'source /relevance-nfs/users/t-raoabhinav/opt/bin/activate; ray stop;';
done
source /relevance-nfs/users/t-raoabhinav/opt/bin/activate; ray stop;