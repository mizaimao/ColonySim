from typing import List, Sequence, Tuple

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, GeomNode, NodePath

from colony.configuration import visual_cfg
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

        self._init_window()  # window settings
        self._init_camera()  # camera settings
        self._init_graphics()  # make graphic-related changes
        self._init_keys()  # key mapping
        self.paint_playground()  # add map and basic objects to screeen
        self.test_location()
        #self.disableMouse()

    def _init_window(self):
        # setup window properties
        properties: WindowProperties = WindowProperties()
        properties.setSize(visual_cfg.panda_width, visual_cfg.panda_height)
        self.win.requestProperties(properties)

    def _init_camera(self):
        self.camera.setPos(0, -100, 0)
        self.camera.lookAt(0.0, 0.0, 0.0)
        # Tilt the camera down by setting its pitch.
        #self.camera.setP(-90)

    def _init_graphics(self):
        pass

    def paint_playground(self):
        # setup background
        self.set_background_color(pColor(visual_cfg.stage_background))


    def test_location(self):
        # snode: GeomNode = make_a_cube()
        
        # cube: NodePath = self.render.attachNewNode(snode)
        # # OpenGl by default only draws "front faces" (polygons whose vertices are
        # # specified CCW).
        scalar: float = 1.

        # cube.setTwoSided(True)
        # cube.setPos(0, 0, 0)
        # cube.setScale(scalar, scalar, scalar)

        snode2: GeomNode = make_a_cube()
        cube2: NodePath = self.render.attachNewNode(snode2)
        cube2.setTwoSided(True)
        cube2.setPos(0, 10, 0)
        cube2.setScale(scalar, scalar, scalar)



panda_viewer: PandaViewer = PandaViewer()
panda_viewer.run()