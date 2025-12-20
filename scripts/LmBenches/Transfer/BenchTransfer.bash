#b=EgoSchema        # 500qa,500v
#b=LongTimeScope    # 450qa,450v
#b=LongVideoBench   #1202qa,618v
#b=LVBench          #1549qa,103v
#b=MLVU              #2592qa,1659v
#b=Video_MME        #2700qa,900v
#b=EgoLifeQA        #500qa, 1v   #actually 3000qa, 6v, only 500 qa released 
b=EgoR1Bench       #300qa, 6v
#b=XLeBench         #1000qa, 100v

python $(dirname "${BASH_SOURCE[0]}")/BenchTransfer.py $b 