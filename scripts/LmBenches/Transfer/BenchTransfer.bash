#b=egoschema        # 500qa,500v
#b=LongTimeScope    # 450qa,450v
#b=LongVideoBench   #1202qa,618v
#b=LVBench          #1549qa,103v
b=MLVU              #2592qa,1659v
#b=Video_MME        #2700qa,900v

python $(dirname "${BASH_SOURCE[0]}")/BenchTransfer.py $b 