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

import Queue

class Segment:
    def __init__(self, msg, dst, altBit):

        # We represent ACK as '<ACK>' in the msg;
        # under alternating-bit protocol NAK is just
        # an ACK for the wrong alternating bit
        self.msg = msg
        self.dst = dst
        
        # The alternating 'bit' used for that protocol
        # represented as a BOOLEAN VALUE
        self.altBit = altBit



class NaiveSender(BaseSender):
    def __init__(self, app_interval):
        super(NaiveSender, self).__init__(app_interval)

    def receive_from_app(self, msg):
        seg = Segment(msg, 'receiver')
        self.send_to_network(seg)

    def receive_from_network(self, seg):
        pass    # Nothing to do!

    def on_interrupt():
        pass    # Nothing to do!

class NaiveReceiver(BaseReceiver):
    def __init__(self):
        super(NaiveReceiver, self).__init__()

    def receive_from_client(self, seg):
        self.send_to_app(seg.msg)



# Alternating-bit protocol
# ========================
class AltSender(BaseSender):
    #TODO
    pass

class AltReceiver(BaseReceiver):
    def __init__(self):
        super(AltReceiver, self).__init__()
        self.altBit = False
        # messageNumber is the alternating 'bit' for which we wait
    
    def receive_from_client(self, seg):
        if "<CORRUPTED>" in seg.msg:
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
                # ...and update our own state
                self.altBit = not self.altBit

            else:
                # Message is of wrong bit, so send opposite ACK
                out = Segment('<ACK>', 'sender', not self.altBit)
                self.send_to_network(out)





class GBNSender(BaseSender):
    # TODO: fill me in!
    pass

class GBNReceiver(BaseReceiver):
    # TODO: fill me in!
    pass
