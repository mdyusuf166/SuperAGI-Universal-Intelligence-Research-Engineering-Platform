from ..models import Connection
def connect(source_id, target_id, weight, delay=0.0): return Connection(source_id=source_id,target_id=target_id,weight=weight,delay=delay)
