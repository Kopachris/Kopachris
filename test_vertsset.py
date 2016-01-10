class Vertex:
    def __init__(self, co):
        self.co = co
        self._private = "_private is usually treated as private"
    def __repr__(self):
        return "<Vertex object with coords {}>".format(self.co)
    def __eq__(self, other):
        if self.co == other.co:
            return True
        else:
            return False
    def __hash__(self):
        return self.co
verts = set()
verts.add(Vertex(1))
verts.add(Vertex(2))
verts.add(Vertex(1))
print(verts)
vert_list = list(verts)
vert_list[0].co = 2
verts = set(vert_list)
print(verts)
print(vert_list[0]._private)
