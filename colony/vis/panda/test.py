import sys
from typing import List, Sequence, Tuple

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec4, WindowProperties, GeomNode, NodePath

from colony.configuration import visual_cfg
from colony.configs.map_generator.ref import map_ref
from colony.vis.panda.cube import make_a_cube


def pColor(color: Sequence[int], BGR: bool = True) -> List[int]:
    """
    Convert RGB or RGBA color to float-based format that is used by
    Panda3D package.
    BGR toggled to true because all previous codes were using BGR (damn opencv).
    """
    converted: List[int] = [c / 255 for c in color]
    if BGR:
        converted[0], converted[2] = converted[2], converted[0]
    return converted


class PandaViewer(ShowBase):
    """
    Customized 3D render inherited from panda3D object.
    """
    def __init__(self):
        """Constructor."""
        super().__init__(self)

        self.root = self.render.attachNewNode("Root")
        self.root.setPos(0.0, 0.0, 0.0)

        self._init_window()  # window settings
        self._init_camera()  # camera settings
        self._init_lighting()
        self._init_graphics()  # make graphic-related changes
        self._init_keys()  # key mapping
        self.paint_playground()  # add map and basic objects to screeen
        self.test_location()

        # this is needed in order to control camera by keyboard
        self.disableMouse()

    def _init_window(self):
        # setup window properties
        properties: WindowProperties = WindowProperties()
        properties.setSize(visual_cfg.panda_width, visual_cfg.panda_height)
        self.win.requestProperties(properties)

    def _init_camera(self):
        self.camera.setPos(0, 0, 0)
        self.camera.lookAt(0.0, 0.0, 0.0)
        self.camLens.setNearFar(1.0, 50.0)
        self.camLens.setFov(45.0)
        # Tilt the camera down by setting its pitch.
        #self.camera.setP(-90)

    def _init_lighting(self):
        self.ambientLight = self.render.attachNewNode(
            AmbientLight("ambient light")
        )
        self.ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.render.setLight(self.ambientLight)

        self.mainLight = self.render.attachNewNode(
            DirectionalLight("main light")
        )
        # Turn it around by 45 degrees, and tilt it down by 45 degrees
        self.mainLight.setHpr(45, -45, 0)
        self.render.setLight(self.mainLight)

    def _init_keys(self):
        self.accept("d", self.move, [1.0, 0.0, 0.0])
        self.accept("a", self.move, [-1.0, 0.0, 0.0])
        self.accept("w", self.move, [0.0, 1.0, 0.0])
        self.accept("s", self.move, [0.0, -1.0, 0.0])
        self.accept("e", self.move, [0.0, 0.0, 1.0])
        self.accept("q", self.move, [0.0, 0.0, -1.0])

    def _init_graphics(self):
        
        pass

    def move(self, x, y, z):
        self.camera.setX(self.camera.getX() + x)
        self.camera.setY(self.camera.getY() + y)
        self.camera.setZ(self.camera.getZ() + z)

    def paint_playground(self):
        # setup background
        self.set_background_color(pColor(visual_cfg.stage_background))


    def test_location(self):
        scalar: float = 1.

        snode: GeomNode = make_a_cube()
        cube: NodePath = self.render.attachNewNode(snode)
        # OpenGl by default only draws "front faces" (polygons whose vertices are
        # specified CCW).
        cube.setTwoSided(True)
        cube.setPos(0, 10, 0)
        cube.setScale(scalar, scalar, scalar)

        # test color setup
        c: Tuple[int, int, int] = pColor(map_ref[1][-1])
        cube.setColor(*c)


panda_viewer: PandaViewer = PandaViewer()
panda_viewer.run()