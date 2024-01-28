'''
Let's try to figure out a way to sync meal records across tablets in real-time. For the sake of centralizing the process, the server acts as a mediator between the tablets. This would be to help ensure that the records are in the same order and state at (approximately) all times (think why this is desirable). This problem implements a tiny local example, where tablets and server are represented by separate objects in the same piece of code. 

Modeling the example 
1. A tablet records a meal (in the real world, this happens when a student taps an ICard or the InstiApp QR code is scanned), and sends that update to the server. In the given code template, the tapping process is replaced by a function generating dummy but unique data. 
2. From the server, the tablet expects updates based on the data the server has aggregated from all tablets (including those from the receiving tablet itself), in the order that the server promises it to be across all the tablets in this session. 

Your task 
Your job is to implement the SyncService class. Don't forget what the server is promising in it's behavior! Checkout the attached code to understand more and start implementing
'''

import random
import datetime
import uuid




# OBJECTIVES TODO:
# 1) Read the code and understand it.
# 2) Read the code again and understand it better.
# 3) Feel free to do 1 and 2 however many times you feel like.
# 4) Complete the SyncService implementation. Note that the SyncService.onMessage and SyncService.__init__ function signature must not be altered.




_DATA_KEYS = ["a","b","c"]
class Device:
    def __init__(self, id):
        self._id = id
        self.records = []
        self.sent = []


    def obtainData(self) -> dict:
        """Returns a single new datapoint from the device.
        Identified by type `record`. `timestamp` records when the record was sent and `dev_id` is the device id.
        `data` is the data collected by the device."""
        if random.random() < 0.4:
            # Sometimes there's no new data
            return {}
        
        # print("obtaining failed")


        rec = {
            'type': 'record', 'timestamp': datetime.datetime.now().isoformat(), 'dev_id': self._id,
            'data': {kee: str(uuid.uuid4()) for kee in _DATA_KEYS}
        };self.sent.append(rec)
        
        #print("Obtained data",end=" ")
        #print(rec)
        
        return rec


    def probe(self) -> dict:
        """Returns a probe request to be sent to the SyncService.
        Identified by type `probe`. `from` is the index number from which the device is asking for the data."""
        if random.random() < 0.5:
            # Sometimes the device forgets to probe the SyncService
            
            #print("probing failed")
            return {}

        pr={'type': 'probe', 'dev_id': self._id, 'from': len(self.records)}
        #print("probing sucessful ",end=" ")
        print(pr)


        return pr 


    def onMessage(self, data: dict):
        """Receives updates from the server"""
        if random.random() < 0.6:
            # Sometimes devices make mistakes. Let's hope the SyncService handles such failures.
            return
        
        if data==None or data == {}:
            return


        if data['type'] == 'update':
            _from = data['from']
            if _from > len(self.records):
                return
            self.records = self.records[:_from] + data['data']





class SyncService:
    def __init__(self):
        self.server_records=[]
        
       
    def onMessage(self, data: dict):

        """Handle messages received from devices.
        Return the desired information in the correct format (type `update`, see Device.onMessage and testSyncing to understand format intricacies) in response to a `probe`.
        No return value required on handling a `record`."""

        if data==None or data == {}:
            return
        elif data['type'] == 'record':
            self.server_records.append(data)
        elif data['type'] == 'probe':
            from_index = data.get('from', 0)
            update_data = self.server_records[from_index:]
            return {'type': 'update', 'from': from_index, 'data': update_data}
        else:
            raise NotImplementedError()








def testSyncing():
    devices = [Device(f"dev_{i}") for i in range(3)]
    syn = SyncService()
   
    _N = int(3)
    for i in range(_N):
        for _dev in devices:
            syn.onMessage(_dev.obtainData())
            _dev.onMessage(syn.onMessage(_dev.probe()))


    done = False
    while not done:
        for _dev in devices: _dev.onMessage(syn.onMessage(_dev.probe()))
        num_recs = len(devices[0].records)
        done = all([len(_dev.records) == num_recs for _dev in devices])


    ver_start = [0] * len(devices)
    for i,rec in enumerate(devices[0].records):
        _dev_idx = int(rec['dev_id'].split("_")[-1])
        assertEquivalent(rec, devices[_dev_idx].sent[ver_start[_dev_idx]])
        for _dev in devices[1:]:
            assertEquivalent(rec, _dev.records[i])
        ver_start[_dev_idx] += 1
    
    
    print(len(syn.server_records))
    print([len(devices[i].records) for i in range(3)])

    def check(list):  # this is to check the validity of our implementation by checking if all the devices have common records that have been given to them by the server using update for which they requested using probe.
        return all(i == list[0] for i in list)

    l=[devices[i].records for i in range(3)]
    l.append(syn.server_records)

    print(check(l))


   

def assertEquivalent(d1:dict, d2:dict):
    assert d1['dev_id'] == d2['dev_id']
    assert d1['timestamp'] == d2['timestamp']
    for kee in _DATA_KEYS:
        assert d1['data'][kee] == d2['data'][kee]

testSyncing()

