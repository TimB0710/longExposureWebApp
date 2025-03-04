import numpy as np

class Point:
    def __init__(self, pos, group, frame):
        self.pos = pos
        self.group = group
        self.frame = frame

    def set_group(self,group):
        self.group = group
    
    def get_dist(self,p2):
        return np.linalg.norm(np.array(self.pos) - np.array(p2.pos))
    
    def get_dist_with_time(self,p2):
        t1 = np.array([self.pos[0],self.pos[1],self.frame])
        t2 = np.array([p2.pos[0],p2.pos[1],p2.frame])
        return np.linalg.norm(np.array(t1) - np.array(t2))

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f"Point[pos:{self.pos},group:{self.group},frame:{self.frame}]"