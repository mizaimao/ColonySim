"""
Codes to build cubes for panda3D, therefore no need to load any assets from
disk.

These crappy codes were based on official sample script:
https://github.com/panda3d/panda3d/blob/master/samples/procedural-cube/main.py
"""
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import GeomNode

from panda3d.core import LVector3

# You can't normalize inline so this is a helper function
def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec

# helper function to make a square given the Lower-Left-Hand and
# Upper-Right-Hand corners
def makeSquare(x1, y1, z1, x2, y2, z2):
    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData('square', format, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    # make sure we draw the sqaure in the right plane
    if x1 != x2:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y1, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y2, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y2 - 1, 2 * z2 - 1))

    else:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y2, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y1, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z2 - 1))

    # adding different colors to the vertex for visibility
    color.addData4f(1.0, 0.0, 0.0, 1.0)
    color.addData4f(0.0, 1.0, 0.0, 1.0)
    color.addData4f(0.0, 0.0, 1.0, 1.0)
    color.addData4f(1.0, 0.0, 1.0, 1.0)

    texcoord.addData2f(0.0, 1.0)
    texcoord.addData2f(0.0, 0.0)
    texcoord.addData2f(1.0, 0.0)
    texcoord.addData2f(1.0, 1.0)

    # Quads aren't directly supported by the Geom interface
    # you might be interested in the CardMaker class if you are
    # interested in rectangle though
    tris = GeomTriangles(Geom.UHDynamic)
    tris.addVertices(0, 1, 3)
    tris.addVertices(1, 2, 3)

    square = Geom(vdata)
    square.addPrimitive(tris)
    return square


def make_a_cube(side: float = 2.) -> GeomNode:
    """
    NOTE: it isn't particularly efficient to make every face as a separate Geom.
    instead, it would be better to create one Geom holding all of the faces.
    """
    hs: float = side / 2  # half side
    square0 = makeSquare(-hs, -hs, -hs, hs, -hs, hs)
    square1 = makeSquare(-hs, hs, -hs, hs, hs, hs)
    square2 = makeSquare(-hs, hs, hs, hs, -hs, hs)
    square3 = makeSquare(-hs, hs, -hs, hs, -hs, -hs)
    square4 = makeSquare(-hs, -hs, -hs, -hs, hs, hs)
    square5 = makeSquare(hs, -hs, -hs, hs, hs, hs)
    snode = GeomNode('square')
    snode.addGeom(square0)
    snode.addGeom(square1)
    snode.addGeom(square2)
    snode.addGeom(square3)
    snode.addGeom(square4)
    snode.addGeom(square5)

    return snode


def make_a_cuboid(
        side_x: float = 2., side_y: float = 2., side_z: float = 2.
    ) -> GeomNode:
    """Make a cubuid with 3 args corresponding to length on each dim.
    """
    hx: float = side_x / 2
    hy: float = side_y / 2
    hz: float = side_z / 2

    square0 = makeSquare(-hx, -hy, -hz, hx, -hy, hz)
    square1 = makeSquare(-hx, hy, -hz, hx, hy, hz)
    square2 = makeSquare(-hx, hy, hz, hx, -hy, hz)
    square3 = makeSquare(-hx, hy, -hz, hx, -hy, -hz)
    square4 = makeSquare(-hx, -hy, -hz, -hx, hy, hz)
    square5 = makeSquare(hx, -hy, -hz, hx, hy, hz)

    snode = GeomNode('square')
    snode.addGeom(square0)
    snode.addGeom(square1)
    snode.addGeom(square2)
    snode.addGeom(square3)
    snode.addGeom(square4)
    snode.addGeom(square5)

    return snode
