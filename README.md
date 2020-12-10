# Decentralized (P2P) Secret Santa

Got sent this [Math StackExchange post](https://math.stackexchange.com/questions/2896780/secret-santa-algorithm-that-does-not-rely-on-a-trusted-3rd-party) by [@ArthurG](https://github.com/ArthurG) and thought I'd give a shot at implementing a small demo of the algorithm presented in the [first answer](https://math.stackexchange.com/a/2897431).
Part of the motivation was that I was unconvinced by some parts of the algorithm (in particular, the technical details of the sub-algorithm, but see [discussion](#Discussion)), but it turned out to be much nicer than expected.

We make a lot of simplifying assumptions in our implementation of this small demo.
What I'd imagine this algorithm becoming is essentially a protocol that actors within the P2P network follow.
Of course, we weren't about to create the entire infrastructure and framework for a mini demo, but it mimics what we'd want while living on a single thread.

## Usage
**Requirements:** Python 3.6.9, though anything 3.X would probably work. Feel free to try Python 2.X (It will likely not work, so do not hold me responsible)

**Example:** Run `python run.py` or make your own modifications to the script

## Discussion
The goal here is to do a deeper dive into some of the technical details (not necessarily _implementation_ details, but mathematical details as well) of the algorithm.
I found that although every step of the algorithm seems straightforward, there's a lot of hidden aspects and gotchas to look out for.
And, a lot of them also lead to nice mathematical discussions (which is right up my alley).

Technical discussion aside for a bit, I just want to mention that this algorithm is really cool.
The more I read into it and the more I think about, the more I like it and the more I've come to appreciate it.
Do not be fooled, there's a lot more to it than just cryptography.
One really has to think hard about decentralized systems and anonymity for this problem and within this algorithm.
I have to tip my hat to the author because there's just such a huge variety of fields of computer science being incorporated into this algorithm.
But precisely because there are so many moving pieces, we should be  a bit careful and slowly our time to understand every individual component.
By no means will I go through everything, but hopefully the reader can walk away a slightly deeper understanding of this algorithm and the concepts related to it.

### Successful Decryptions
We start with something that feels very simple on paper.
In step 5 of the sub-algorithm, the author tells us to perform the following: _"Publish all contents where decryption succeeds"_.
This is a very innocent statement, but what the heck does it mean for a decryption to be successful?
This seems simple if you're encrypting/decrypting readable messages, say for example, the sentence: "A quick brown fox jumps over the lazy dog".
A decryption is successful when the message makes sense.

But, we're not encrypting readable messages here.
We're encrypting keys, which are (probably) going to look like garbage.
It also doesn't help that part of our algorithm will encrypt the garbage _multiple_ times.
So how do we know that we've decrypted the right garbage?

My first idea was super simple.
Let's just append the same phrase to the end of every message and validate that this message exists after decryption.
Is this secure?
Probably not.
(Didn't stop me from implementing it, but that's besides the point :P)
It motivates the idea though, that we want some sort of a signature that we can verify the decryption against.

Indeed, this led me directly to the 2nd idea of appending on a hash of the plaintext onto the ciphertext.
Verifying that the decryption is successful is easy, just hash the decrypted plaintext and see if matches what we appended.
This is now closer to what is used in practice, which is a scheme called [OAEP](https://en.wikipedia.org/wiki/Optimal_asymmetric_encryption_padding).

Imagine my surprise when I was trying to implement this success checker and I receive an exception in my code from this scheme.
I was completely unaware that this scheme existed (actually, now that I think about it, it _may_ have mentioned in lectures, but .... :P).
In my mind though, I had only ever thought about using textbook RSA.
Nevertheless, this was a very nice finding and certainly made the implementation a bit easier to do.

### Faulty Onion Routing

In the sub-algorithm, we perform a series of iterated encryptions that mimics onion routing (technique used by software like Tor).
I understood the technique but was unconvinced that it would work in our setting. 
Turns out, an implementation detail will once again mitigate the problem for us, but the following will be a nice thought experiment nonetheless.

The issue that I thought would occur is that publishing messages publicly (encrypted or not) means that everyone can see the history of the messages.
This makes the entire sub-algorithm useless since if I've published that I've decrypted a message, anyone can easily re-encrypt it using my public key and then find a match in the history.
Continuing this process, we can always work backwards to find the originator of any message.

This assumes a public log of all messages, which may not necessarily be the case.
Perhaps all we have is the log we can create from messages being sent to us.
In this case, we have a better chance of mitigating this issue.
We just can't use a fully-connected distributed network.
For example, if we only passed messages along a cycle, and could record that a message came from our predecessor, then it becomes impossible to "work backwards" through the history.
A more complicated example might have us in a random network where we are randomly connected to our peers.
This will also work, but we do have to deal with the issue of knowing when everyone has received any particular message.
(Note that is easy within the cycle, since we'll always go back to the original message sender)

All this said though, once again, OAEP comes in and says: "AHA, we've already thought about this! What if encryption was non-deterministic?"
That's all it takes to stop us from "working backwards", since the encryptions will also yield different outcomes.
Nonetheless, it was fun to think about algorithm in the sense of distributed networks and it really goes to show just how nicely it handles complex cases like this.

### Iterated Encryption Blowup

This last detail is strictly implementation-related and something I found out while coding up the algorithm.
Since our particular cipher uses OAEP, some amount of bytes are reserved for the creating the padding.
This means that our chunks have to be slightly smaller than the size of the RSA modulus, but they will always grow to the size of the modulus after encryption.
As such, the message length under iterated encryptions will grow in size.
For reference, after 9 iterated encryptions (using the settings in our files), an original message of 450 bytes grew to 4608 bytes.
One could figure the actual growth, but even with small example, it demonstrates that this method doesn't scale well with the number of actors.

There's not much more to say here.
For the scale of this demo, this fact didn't make difference, but there's a clear practical concern.
I tried to think of other schemes but didn't dwell on this problem for too long.