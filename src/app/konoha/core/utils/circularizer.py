import numpy as np
from PIL import Image, ImageDraw, ImageOps

class Circularizer:
    def __init__(self, r, images=None):
        self.images = images
        self.N = len(r)
        self.x = np.ones((self.N,3))
        self.x[:,2] = r
        maxstep = 2*self.x[:,2].max()
        length = np.ceil(np.sqrt(self.N))
        grid = np.arange(0,length*maxstep,maxstep)
        gx,gy = np.meshgrid(grid,grid)
        self.x[:,0] = gx.flatten()[:self.N]
        self.x[:,1] = gy.flatten()[:self.N]
        self.x[:,:2] = self.x[:,:2] - np.mean(self.x[:,:2], axis=0)

        self.step = self.x[:,2].min()
        self.p = lambda x,y: np.sum((x**2+y**2)**2)
        self.E = self.energy()
        self.iter = 1.

    def minimize(self):
        while self.iter < 100*self.N:
            for i in range(self.N):
                rand = np.random.randn(2)*self.step/self.iter
                self.x[i,:2] += rand
                e = self.energy()
                if (e < self.E and self.isvalid(i)):
                    self.E = e
                    self.iter = 1.
                else:
                    self.x[i,:2] -= rand
                    self.iter += 1.

    def energy(self):
        return self.p(self.x[:,0], self.x[:,1])

    def distance(self,x1,x2):
        return np.sqrt((x1[0]-x2[0])**2+(x1[1]-x2[1])**2)-x1[2]-x2[2]

    def isvalid(self, i):
        for j in range(self.N):
            if i!=j: 
                if self.distance(self.x[i,:], self.x[j,:]) < 0:
                    return False
        return True

    def plot(self, size=512):
        sz = (self.x[:, :2] + self.x[:, 2:]).max(axis=0) - (self.x[:, :2] - self.x[:, 2:]).min(axis=0)
        x = self.x.copy()
        x[:, 0] -= ((x[:, 0] + x[:, 2]).max() + (x[:, 0] - x[:, 2]).min()) / 2
        x[:, 1] -= ((x[:, 1] + x[:, 2]).max() + (x[:, 1] - x[:, 2]).min()) / 2
        r = size * 0.9 / sz.max()
        coords = (x * r).astype(np.int32)
        img = Image.new('RGBA', (size, size))
        for i, image in enumerate(self.images):
            x, y, r = coords[i]
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            if 2*r < (size // 64):
                continue
            image = image.resize((2*r, 2*r))
            mask = mask.resize((2*r, 2*r))
            image.putalpha(mask)
            img.paste(image, (x+size//2-r, y+size//2-r), image)
        return img

if __name__ == "__main__":
    r = np.random.randint(5, 100, size=10) / 100
    c = Circularizer(r)
    c.minimize()
    print(c.x)
    print(c.plot())