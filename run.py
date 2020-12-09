from lib.SecretSanta import SecretSanta

ss = SecretSanta()
ss.registerUser('billy')
ss.registerUser('bob')
ss.registerUser('joe')
ss.registerUser('moses')
ss.initializeNetwork()
ss.createDerangement()
