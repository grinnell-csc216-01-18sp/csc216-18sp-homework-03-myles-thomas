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

# N.B. on timeouts: Even with a network delay of 0, app-delay of 5 is needed
# (in Alternating bit protocol at least) to ensure everything given by the
# application layer is sent

# The timeout for the Alternating bit protocol
ALT_BIT_INTERVAL = 5


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
        seg = Segment(msg, 'receiver', False) # altBit ignored
        self.send_to_network(seg)

    def receive_from_network(self, seg):
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
            # TODO:Tell the application layer it cannot send any more messages
            #self.disallow_app_msgs()
            # Send the message [and store it for resending]
            self.out = Segment(msg, 'receiver', self.altBit)
            self.send_to_network(self.out)
            # Update our state
            self.state = not self.state
            # Start the timer
            self.start_timer(ALT_BIT_INTERVAL)
    
    def receive_from_network(self, seg):
        # if we are awaiting network message
        if not self.state:
            if (not '<CORRUPTED>' in seg.msg) and seg.altBit == self.altBit:
                # Message is noncorrupted and valid, so:
                # Stop the timer
                self.end_timer()
                # Update our state to waiting for app
                self.state = not self.state
                # Toggle our bit
                self.altBit = not self.altBit
                # TODO:Clear the application layer for sending the next message
                #self.allow_app_msgs()


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
    # TODO: fill me in!
    pass

class GBNReceiver(BaseReceiver):
    # TODO: fill me in!
    pass
