from lib.SecretSanta import SecretSanta

# Create the game
ss = SecretSanta()

# Register users
ss.registerUser('Nayeon')
ss.registerUser('Jeongyeon')
ss.registerUser('Momo')
ss.registerUser('Sana')
ss.registerUser('Jihyo')
ss.registerUser('Mina')
ss.registerUser('Dahyun')
ss.registerUser('Chaeyoung')
ss.registerUser('Tzuyu')

# Initialize
ss.initializeNetwork()

# Perform the algorithm
ss.createDerangement()
