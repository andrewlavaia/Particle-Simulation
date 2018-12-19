class WorkRequest():
    def __init__(self, particle_index, time, limit, particles, walls):
        self.particle_index = particle_index
        self.time = time 
        self.limit = limit
        self.particles = particles
        self.walls = walls