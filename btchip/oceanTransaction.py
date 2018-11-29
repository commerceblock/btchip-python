"""
*******************************************************************************
*   BTChip Bitcoin Hardware Wallet Python API
*   (c) 2014 BTChip - 1BTChip7VfTnrPra5jqci7ejnMguuHogTn
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
*   Unless required by applicable law or agreed to in writing, software
*   distributed under the License is distributed on an "AS IS" BASIS,
*   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*   limitations under the License.
********************************************************************************
"""

from .bitcoinVarint import *
from binascii import hexlify
from collections import namedtuple
from electrumx.lib.tx import DeserializerOcean, TxOcean, TxInputOcean, TxOutputOcean

class oceanTransaction(TxOcean):
	def __init__(self, orig:TxOcean=None, binary:bytes=None, start=0):
		#Initialize either with a TxOcean object, or deserialize from bytes
		if orig is None:
			self._non_copy_constructor(binary, start)
		else:
			self._copy_constructor(orig)

	def _copy_constructor(self, orig):
		self.version = orig.version
		self.flag = orig.flag
		self.locktime = orig.locktime
		self.inwitness = orig.inwitness
		self.outwitness = orig.outwitness
		self.inputs=[]
		for inpt in orig.inputs:
			self.inputs.append(oceanInput(inpt))
		self.outputs=[]
		for outpt in orig.outputs:
			self.outputs.append(oceanOutput(outpt))

	def _non_copy_constructor(self, binary, start):
		assert binary is not None
		self._copy_constructor(DeserializerOcean(binary, start).read_tx())
		

	def serialize(self, skipOutputLocktime=False, skipWitness=False):
		if skipWitness or (not self.inwitness and not self.outwitness):
			useWitness = False
		else:
			useWitness = True
		result = []
		result.extend(self.version)
		result.extend(self.flag)
		writeVarint(len(self.inputs), result)
		for trinput in self.inputs:
			result.extend(trinput.serialize())
		if not skipOutputLocktime:
			writeVarint(len(self.outputs), result)
			for troutput in self.outputs:
				result.extend(troutput.serialize())
			result.extend(self.locktime)
			if useWitness:
				result.extend(self.inwitness)
				result.extend(self.outwitness)
		return result

	def serializeOutputs(self):
		result = []
		writeVarint(len(self.outputs), result)
		for troutput in self.outputs:
			result.extend(troutput.serialize())
		return result

class oceanInput(TxInputOcean):
	def __init__(self, orig:TxInputOcean = None):
		if orig is None:
			self._non_copy_constructor()
		else:
			self._copy_constructor(orig)

	def _non_copy_constructor(self):
		self.prev_hash = None
		self.prev_idx = None
		self.script = None
		self.sequence = None
		self.issuance = None

	def _copy_constructor(self, orig:TxInputOcean):
		self.prev_hash = orig.prev_hash
		self.prev_idx = orig.prev_idx
		self.script = orig.script
		self.sequence = orig.sequence
		self.issuance = orig.issuance

	def getScriptLength(self):
		return len(self.script)

	def serialize(self):
		result = []
		result.extend(self.prev_hash)
		result.extend(self.prev_idx)
		writeVarint(self.getScriptLength(), result)
		result.extend(self.script)
		result.extend(self.sequence)
		if self.issuance is not None:
			iss=self.issuance
			result.extend(iss.issuance_none)
			result.extend(iss.issuance_entropy)
			result.extend(iss.amount)
			result.extend(iss.inflation)
		return result

	def __str__(self):
		buf =  "PrevHash : " + hexlify(self.getPrevHash()) + "\r\n"
		buf =  "PrevIdx : " + hexlify(self.getPrevIdx()) + "\r\n"
		buf += "Script : " + hexlify(self.getScript()) + "\r\n"
		buf += "Sequence : " + hexlify(self.getSequence()) + "\r\n"
		buf += "Issuance : " + hexlify(self.getIssuance()) + "\r\n"
		return buf



class oceanOutput(TxOutputOcean):
	def __init__(self, orig:TxOutputOcean=None):
		if orig is None:
			self._non_copy_constructor()
		else:
			self._copy_constructor(orig)

	def _non_copy_constructor(self):
		self.asset = None
		self.value = None
		self.nonce = None
		self.script = None

	def _copy_constructor(self, orig:TxInputOcean):
		self.asset = orig.asset
		self.value = orig.value
		self.nonce = orig.nonce
		self.script = orig.script
		
	def getScriptLength(self):
		return len(self.script)

	def serialize(self):
		result = []
		result.extend(self.asset)
		result.extend(self.value)	
		result.extend(self.nonce)
		writeVarint(self.getScriptLength(), result)
		result.extend(self.script)
		return result

	def __str__(self):
		buf =  "Asset : " + hexlify(self.asset) + "\r\n"
		buf += "Amount : " + hexlify(self.amount) + "\r\n"
		buf += "Nonce : " + hexlify(self.nonce) + "\r\n"
		buf += "Script : " + hexlify(self.script) + "\r\n"
		return buf
