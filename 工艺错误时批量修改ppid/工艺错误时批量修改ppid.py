import pymysql
#ppid数量：
PRODUCT_COUNT = 1
#从末尾往前第几位开始(python会从右向左取序列号的长度)
SEQ_START_FROM_END = 2
#序列号长度
SEQ_LEN = 1

conn = pymysql.connect(
    host='192.168.1.198',
    user='root',
    password='r3xa7z*mjRC',
    database='mom',
    charset='utf8mb4'
)
cursor = conn.cursor()

cursor.execute('''
    SELECT id, ppid
    FROM mps_production_order_ppid_process
    WHERE production_order_no = 'MO-26040269'
    ORDER BY id
''')
rows = cursor.fetchall()
ppid_map = {}
#函数
def revert_ppid(ppid, product_count, seq_start_from_end, seq_len):
    seq_end = len(ppid) - seq_start_from_end + 1
    seq_start = seq_end - seq_len

    prefix = ppid[:seq_start]
    seq = int(ppid[seq_start:seq_end])
    suffix = ppid[seq_end:]
    old_seq = seq - product_count
    if old_seq <= 0:
        return ppid
    return prefix + str(old_seq).zfill(seq_len) + suffix
for id_, ppid in rows:
    old_ppid = revert_ppid(
        ppid,
        PRODUCT_COUNT,
        SEQ_START_FROM_END,
        SEQ_LEN
    )
    print('过站记录表:',ppid, '->', old_ppid)
    ppid_map[ppid] = old_ppid
    cursor.execute('''
        UPDATE mps_production_order_ppid_process
        SET ppid = %s
        WHERE id = %s
    ''', (old_ppid, id_))
cursor.execute('''
   SELECT id, ppid
   FROM mps_production_order_ppid
   WHERE production_order_no = 'MO-26040269'
''')
ppid_rows = cursor.fetchall()
for id_, ppid in ppid_rows:
    if ppid in ppid_map:
        old_ppid = ppid_map[ppid]
        print('ppid工艺表:',ppid, '->', old_ppid)
        cursor.execute('''
            UPDATE mps_production_order_ppid
            SET ppid = %s
            WHERE id = %s
        ''', (old_ppid, id_))
conn.commit()
cursor.close()
conn.close()
