// Start with just doing casanova attest

use std::collections::BTreeSet as Set;
use std::collections::VecDeque;

#[derive(Eq, PartialEq, Debug, Ord, PartialOrd)]
pub struct Event {
    //TODO what actually should go in the events?
    id: u32,
}

#[derive(Eq, PartialEq, Debug, Ord, PartialOrd)]
pub struct Block {
    //TODO I would like these to be sets
    parents: Set<Block>,
    events: Set<Event>,
}

#[derive(Eq, PartialEq, Debug)]
pub struct Validator {
    dag: Set<Block>,
    pending: Set<Block>,
    waiting: Set<Event>,
}

impl Validator {
    /// Validator receives a block from the network and processes it
    pub fn receive_block(&mut self, b: Block) {
        if b.parents.is_subset(&self.dag) {
            // This block is ready to go in the DAG
            let mut q = VecDeque::new();
            q.push_back(b);

            // As long as there are more blocks ready to go in the dag, keep iterating
            while !q.is_empty() {
                if let Some(b) = q.pop_front() {
                    self.dag.insert(b);
                }
                let mut satisfied = self.pending.iter().filter(|b| b.parents.is_subset(&self.dag)).collect::<VecDeque<_>>();
                q.append(&mut satisfied); // This line doesn't compile
            }
        }
        else {
            // Not all parents are in the dag, so
            // Add the block to the pending set
            self.pending.insert(b);
        }
    }

    /// Validator receives an event from a network user
    pub fn receive_event(&mut self, e: Event) {

    }

    /// Validator authors a new block from existing events
    pub fn create_block(&mut self) {
        // Paper calls this time_expire
    }
}

fn main() {
    println!("Hello, world!");
}
