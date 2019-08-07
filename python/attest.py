# This would benefit from proper tests

import random

class Event:
    def __init__(self, parents, payload):
        self.parents = set(parents)
        self.payload = payload

class Block:
    def __init__(self, parents, events):
        """
        Takes any iterable of parents and events and turns them into sets.
        """
        self.parents = set(parents)
        self.events = set(events)

class Validator:
    def __init__(self, name = None):
        self.dag = set()
        self.dagEvents = set()
        self.dagLeaves = set()
        self.pendingBlocks = set()
        self.waitingEvents = set()
        self.name = name if name is not None else "Validator" + str(random.random())[2:]

    def __str__(self):
        template = "Name: {}, DAG: {} blocks, Pending: {} blocks, Waiting: {} events."
        return template.format(self.name, len(self.dag), len(self.pendingBlocks), len(self.waitingEvents))

    def receive_block(self, b):
        if b.parents <= self.dag:
            # This block is ready to go in the dag
            satisfied = {b}
            while len(satisfied) > 0:
                for s in satisfied:
                    self.add_block_to_dag(s)
                satisfied.clear()
                # More blocks might be ready now
                # This is basically just a filter
                for candidate in self.pendingBlocks:
                    if candidate.parents <= self.dag:
                        satisfied.add(candidate)
                self.pendingBlocks -= satisfied
        else:
            # Not all parents are in the dag,
            # so mark it pending
            self.pending.add(b)

    def receive_event(self, e):
        """
        Validator received a new event (transaction) from the network. If all of its
        parents are known, then it goes into the set of waiting events. Otherwise it
        is discarded. Return true if the event was added, false if it was discarded.

        Other validators may know of all the parents and not discard it,
        or it may be re-submitted later after the parents have made it around the network.
        It would also be possible to keep track of events whoe parents aren't yet known in
        the same way we do for blocks, but then junk blocks could gum up the works.
        """
        if e.parents <= (self.waitingEvents | self.dagEvents):
            self.waitingEvents.add(e)
            return True
        return False

    def create_block(self):
        """
        Author a new block with all the waiting events using all the DAGs leaves
        as parents. Returns the newly-authored block.
        """
        newB = Block(self.dagLeaves, self.waitingEvents)
        self.waitingEvents.clear()
        self.add_block_to_dag(newB)

        # This class does not communicate with any network.
        # Instead we'll just return the block for simulation purposes.
        return newB

    def add_block_to_dag(self, b):
        """
        This method does not appear explicitly in the paper.
        It adds a block to the dag and maintains data consistency by
        * Adding the block to the dag set
        * Updates the set of all events in the DAG
        * Updating the set of leaves in the dag
        """
        self.dag.add(b)
        self.dagLeaves.add(b)
        self.dagLeaves -= b.parents
        self.dagEvents.update(b.events)


if __name__ == "__main__":
    # Create two validators
    alice = Validator()
    bob = Validator("Bob_Is_The_Best_Validator")

    # Create four events like this
    #   1   2
    #  / \ / \
    # 3   4  |
    #      \ /
    #       5
    e1 = Event([],       "event one")
    e2 = Event([],       "event two")
    e3 = Event([e1],     "event three")
    e4 = Event([e1, e2], "event four")
    e5 = Event([e4, e2], "event five")

    # Send events 1 and 2 to both validators
    alice.receive_event(e1)
    alice.receive_event(e2)
    bob.receive_event(e1)
    bob.receive_event(e2)

    # Send event 3 to Alice
    alice.receive_event(e3)

    # Sends events 4 and 5 to Bob
    bob.receive_event(e4)
    bob.receive_event(e5)

    # Send e5 to Alice (she should discard it)
    alice.receive_event(e5)

    # Check how many events each validator has
    print(alice) # Expect 3 events
    print(bob)   # Expect 4 events

    # Alice creates a block and sends it to bob
    b1 = alice.create_block()
    bob.receive_block(b1)

    # Check how many blocks each validator has
    print(alice) # Expect 1 block
    print(bob)   # Expect 1 block
