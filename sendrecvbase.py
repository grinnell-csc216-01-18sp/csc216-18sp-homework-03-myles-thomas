##
# CSC 216 (Spring 2018)
# Reliable Transport Protocols (Homework 3)
#
# Sender-receiver base classes (v2).  You should not modify this file as part
# of your homework.
##

import Queue

class BaseSender(object):
    def __init__(self, app_interval):
        self.input_queue     = Queue.Queue()
        self.output_queue    = Queue.Queue()
        self.app_interval    = app_interval
        self.app_timer       = 0
        self.app_count       = 0
        self.custom_enabled  = False
        self.custom_interval = 0
        self.custom_timer    = 0
        self.blocked         = False

    def send_to_network(self, seg):
        self.output_queue.put(seg)

    def disallow_app_msgs(self):
        self.blocked = True

    def allow_app_msgs(self):
        self.blocked = False

    # Added an input to define TCP connections
    def step(self, tcpStatus):
        self.app_timer += 1
        if self.app_timer >= self.app_interval and not self.blocked:
            if tcpStatus == '':
                # normal operation
                self.app_count += 1
                self.receive_from_app('message {}'.format(self.app_count))
            else:
                # special TCP protocol messages
                # just send the message right out the door!
                self.receive_from_app('<{}>'.format(tcpStatus))
            self.app_timer = 0
        if not self.input_queue.empty():
            self.receive_from_network(self.input_queue.get())
        if self.custom_enabled:
            self.custom_timer += 1
            if self.custom_timer >= self.custom_interval:
                self.custom_timer = 0
                self.custom_enabled = False
                self.on_interrupt()

    def start_timer(self, interval):
        self.custom_enabled  = True
        self.custom_interval = interval
        self.custom_timer    = 0

    def end_timer(self):
        self.custom_enabled = False

    def receive_from_app(self, msg):
        pass

    def receive_from_network(self, seg):
        pass

    def on_interrupt(self):
        pass

class BaseReceiver(object):
    def __init__(self):
        self.input_queue    = Queue.Queue()
        self.output_queue   = Queue.Queue()
        self.received_count = 0
        self.appside = '<NOTHING>'
        pass

    def step(self):
        if not self.input_queue.empty():
            self.receive_from_client(self.input_queue.get())
        # Hack to allow Simulation to detect what is sent to app layer 
        # Should cause BaseReceiver step to return whatever it successfully
        # received, or '<NOTHING>' if nothing was received that step
        tickTemp = self.appside
        self.appside = '<NOTHING>'
        return tickTemp

    def send_to_network(self, seg):
        self.output_queue.put(seg)

    def send_to_app(self, msg):
        self.received_count += 1
        print('Message received ({}): {}'.format(self.received_count, msg))
        # Hack to allow Simulation to detect when TCP handshake succeeds
        self.appside = msg       

    def receive_from_client(self, seg):
        pass
