from operator import itemgetter, setitem

class SpeedParameters(tuple):
    'SpeedParameters(max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx,  burst_time_tx, burst_time_rx, min_tx, min_rx,  priority, time_start, length, repeat_after, tariff_id)' 

    __slots__ = () 

    _fields = ('max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx',  'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx',  'priority', 'time_start', 'length', 'repeat_after', 'tariff_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx,  burst_time_tx, burst_time_rx, min_tx, min_rx,  priority, time_start, length, repeat_after, tariff_id):
        return tuple.__new__(cls, (max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx,  burst_time_tx, burst_time_rx, min_tx, min_rx,  priority, time_start, length, repeat_after, tariff_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new SpeedParameters object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 15:
            raise TypeError('Expected 15 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SpeedParameters(max_tx=%r, max_rx=%r, burst_tx=%r, burst_rx=%r, burst_treshold_tx=%r, burst_treshold_rx=%r,  burst_time_tx=%r, burst_time_rx=%r, min_tx=%r, min_rx=%r,  priority=%r, time_start=%r, length=%r, repeat_after=%r, tariff_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'max_tx':t[0], 'max_rx':t[1], 'burst_tx':t[2], 'burst_rx':t[3], 'burst_treshold_tx':t[4], 'burst_treshold_rx':t[5],  'burst_time_tx':t[6], 'burst_time_rx':t[7], 'min_tx':t[8], 'min_rx':t[9], 'priority': t[10], 'time_start': t[11], 'length': t[12], 'repeat_after': t[13], 'tariff_id': t[14]} 

    def _replace(self, **kwds):
        'Return a new SpeedParameters object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx',  'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx',  'priority', 'time_start', 'length', 'repeat_after', 'tariff_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    max_tx = property(itemgetter(0))
    max_rx = property(itemgetter(1))
    burst_tx = property(itemgetter(2))
    burst_rx = property(itemgetter(3))
    burst_treshold_tx = property(itemgetter(4))
    burst_treshold_rx = property(itemgetter(5))
    burst_time_tx = property(itemgetter(6))
    burst_time_rx = property(itemgetter(7))
    min_tx = property(itemgetter(8))
    min_rx = property(itemgetter(9))
    priority = property(itemgetter(10))
    time_start = property(itemgetter(11))
    length = property(itemgetter(12))
    repeat_after = property(itemgetter(13))
    tariff_id = property(itemgetter(14))
