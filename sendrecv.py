##
# CSC 216 (Spring 2018)
# Reliable Transport Protocols (Homework 3)
#
# Sender-receiver code for the RDP simulation program.  You should provide
# your implementation for the homework in this file.
#
# Your various Sender implementations should inherit from the BaseSender
# class which exposes the following important methods you should use in your
# implementations:
#
# - sender.send_to_network(seg): sends the given segment to network to be
#   delivered to the appropriate recipient.
# - sender.start_timer(interval): starts a timer that will fire once interval
#   steps have passed in the simulation.  When the timer expires, the sender's
#   on_interrupt() method is called (which should be overridden in subclasses
#   if timer functionality is desired)
#
# Your various Receiver implementations should also inherit from the
# BaseReceiver class which exposes thef ollowing important methouds you should
# use in your implementations:
#
# - sender.send_to_network(seg): sends the given segment to network to be
#   delivered to the appropriate recipient.
# - sender.send_to_app(msg): sends the given message to receiver's application
#   layer (such a message has successfully traveled from sender to receiver)
#
# Subclasses of both BaseSender and BaseReceiver must implement various methods.
# See the NaiveSender and NaiveReceiver implementations below for more details.
##

from sendrecvbase import BaseSender, BaseReceiver
from copy import deepcopy
import Queue

# The timeout for the Alternating bit protocol
ALT_BIT_INTERVAL = 5

def peek(q):
	return q.queue[0]


class Segment:
	def __init__(self, msg, dst, altBit = True, sequence_number = -1):

		# We represent ACK as '<ACK>' in the msg;
		# under alternating-bit protocol NAK is just
		# an ACK for the wrong alternating bit
		self.msg = msg
		self.dst = dst

		# The alternating 'bit' used for that protocol
		# represented as a BOOLEAN VALUE
		self.altBit = altBit

		# The sequence number of the packet
		# used by the GBN protocol
		self.sequence_number = sequence_number

		# For the Mastery Component, since we aren't using
		# sequence numbers, SYN will be represented in the
		# message as "<SYN>", SYNACK as "<SYNACK>" and
		# the third message as "<SYNACKACK>".
		# Mastery component control handled by Simulation





class NaiveSender(BaseSender):
	def __init__(self, app_interval):
		super(NaiveSender, self).__init__(app_interval)

	def receive_from_app(self, msg):
		seg = Segment(msg, 'receiver') # altBit ignored
		self.send_to_network(seg)

	def receive_from_network(self, seeg):
		pass    # Nothing to do!

	def on_interrupt(self):
		pass    # Nothing to do!

class NaiveReceiver(BaseReceiver):
	def __init__(self):
		super(NaiveReceiver, self).__init__()

	def receive_from_client(self, seg):
		self.send_to_app(seg.msg)



# Alternating-bit protocol
# ========================
class AltSender(BaseSender):
	def __init__(self, app_interval):
		super(AltSender, self).__init__(app_interval)

		self.state = True
		# states:
		# True = waiting for application layer
		# False = waiting for ACK
		# whether 0 or 1 is awaited is determined by self.altBit (below)

		# the alternating 'bit' for which we wait
		self.altBit = False

		# persistent storage for each message if it needs resending
		self.out = Segment('', 'receiver', self.altBit)

	def receive_from_app(self, msg):
		# if we are ready to receive from application layer
		if self.state:
			# Tell the application layer it cannot send any more messages
			self.disallow_app_msgs()
			# Send the message [and store it for resending]
			self.out = Segment(msg, 'receiver')
			self.send_to_network(self.out)
			# Update our state
			self.state = not self.state
			# Start the timer
			self.start_timer(ALT_BIT_INTERVAL)


	def receive_from_network(self, seg):
		if not self.state:
			if (not '<CORRUPTED>' in seg.msg) and seg.altBit == self.altBit:
				# Message is noncorrupted and valid, so:
				# Stop the timer
				self.end_timer()
				# Update our state to waiting for app
				self.state = not self.state
				# Toggle our bit
				self.altBit = not self.altBit
				# Clear the application layer for sending the next message
				self.allow_app_msgs()


	def on_interrupt(self):
		# if we are in fact in wait mode
		if not self.state:
			# Re-send the packet and restart the timer
			self.send_to_network(self.out)
			self.start_timer(ALT_BIT_INTERVAL)


class AltReceiver(BaseReceiver):
	def __init__(self):
		super(AltReceiver, self).__init__()
		self.altBit = False
		# messageNumber is the alternating 'bit' for which we wait

	def receive_from_client(self, seg):
		if '<CORRUPTED>' in seg.msg:
			# Corrupted message, so we send an ACK of the opposite bit
			out = Segment('<ACK>', 'sender', not self.altBit)
			self.send_to_network(out)
		else:

			# Message is not corrupt but may be incorrect bit
			if self.altBit == seg.altBit:
				# Message is of awaited bit, so deliver it...
				self.send_to_app(seg.msg)
				# ...then send the true ACK...
				out = Segment('<ACK>', 'sender', self.altBit)
				self.send_to_network(out)
				# ...and update our own state
				self.altBit = not self.altBit

			else:
				# Message is of wrong bit, so send opposite ACK
				out = Segment('<ACK>', 'sender', not self.altBit)
				self.send_to_network(out)


class GBNSender(BaseSender):
	def __init__(self, app_interval):
		super(GBNSender, self).__init__(app_interval)
		self.oldest = 1
		self.next_sequence = 2
		self.max = 3
		self.queue = Queue.Queue()

	def receive_from_app(self, msg):
		seg = Segment(msg, 'receiver', None, self.next_sequence)
		self.queue.put(seg)
		self.send_to_network(deepcopy(seg))
		self.next_sequence += 1
		if self.queue.qsize() == self.max:
			self.disallow_app_messages()
		if self.queue.qsize() == 1:
			self.start_timer(15)

	def receive_from_network(self, seg):
		if seg.msg == '<ACK>' and seg.sequence_number > self.oldest:
			self.oldest = seg.sequence_number
			while not self.queue.empty() and peek(self.queue).sequence_number < self.oldest:
				self.queue.get()
			self.allow_app_messages()

	def on_interrupt(self):
		for seg in list(self.queue.queue):
			self.send_to_network(deepcopy(seg))
		self.start_timer(15)


class GBNReceiver(BaseReceiver):
	def __init__(self):
		super(GBNReceiver, self).__init__()
		self.newest_sequence = 1

	def receive_from_client(self, seg):
		if seg.msg != '<CORRUPTED>' and seg.sequence_number == self.newest_sequence + 1:
			self.newest_sequence += 1
			self.send_to_app(seg.msg)
			seg2 = Segment('<ACK>', 'sender', None, self.newest_sequence)
		else:
			seg2 = Segment('<ACK>', 'sender', None, self.newest_sequence)
		self.send_to_network(seg2)

