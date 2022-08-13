import sys
from typing import Dict, List, Sequence, Tuple

import numpy as np

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, Camera, DirectionalLight, Vec4, WindowProperties, GeomNode, NodePath, OrthographicLens

from colony.characters.colony import Colony
from colony.configuration import visual_cfg, MapSetup, map_cfg
from colony.configs.map_generator.ref import map_ref
from colony.vis.panda.cube import make_a_cube, make_a_cuboid
from colony.characters.spore import Spore, ColonySporeManager


# center of playboard, used as a multi-purpose reference
CENTER: Tuple[float, float, float] = (0, 0, 0)


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


def calculate_dimetric_angle(
        l: float,
        reference: Tuple[float, float, float] = None,
    ) -> Tuple[float, float, float]:
    """
    Calculate camera position given distance between camera and reference point.
    """
    if not reference:
        reference = CENTER
    sqrt_2: float = np.sqrt(2)
    sqrt_6: float = np.sqrt(6)
    # relative location to point (0, 0, 0)
    rel_location: Tuple[float, float, float] = (
        (sqrt_6 / 4) * l,
        - (sqrt_6 / 4) * l,
        l / 2
    )
    abs_location: Tuple[float, float, float] = (
        rel_location[0] + reference[0],
        rel_location[1] + reference[1],
        rel_location[2] + reference[2]
    )
    print(abs_location)
    return abs_location


class PandaViewer(ShowBase):
    """
    Customized 3D render inherited from panda3D object.
    """
    def __init__(self, colony: Colony = None):
        """Constructor."""
        super().__init__(self)

        self.colony: Colony = colony
        # playground array
        self.bitmap: np.ndarray = map_cfg.bitmap
        # playground object
        self.playboard: NodePath
        # playground size
        self.pg_size: Tuple[int, int, int] = (8, 8, 0.2)
        self.cube_x: float
        self.cube_y: float
        self.cube_z: float

        # tracker for each spore by their ids, used in operations like spore deletion
        self.spore_tracker: Dict[int, NodePath] = {}

        # self.root = self.render.attachNewNode("Root")
        # self.root.setPos(0.0, 0.0, 0.0)

        self._init_window()  # window settings
        self._init_camera()  # camera settings
        self._init_lighting()  # lighting pos, etc.
        self._init_graphics()  # make graphic-related changes
        self._init_keys()  # key mapping

        # calcualte needed multipliers for visual mapping purposes.
        # E.g. mapping sizes of spores in relate to playboard size.
        self._figure_out_multiplier()

        self.paint_playground()  # add map and basic objects to screeen
        #self.test_location()
        self.add_initial_players()

        # this is needed in order to control camera by keyboard
        self.disableMouse()

    def _init_window(self):
        """Set up window properties."""
        properties: WindowProperties = WindowProperties()
        properties.setSize(visual_cfg.panda_width, visual_cfg.panda_height)
        self.win.requestProperties(properties)

    def _init_camera(self):
        """Set up camera location and direction."""
        scalar: float = 1.2
        length: int = 5

        # top-down view
        # self.camera.setPos(0, 0, 20)
        # self.camera.lookAt(0.0, 0.0, 0.0)

        # dimetric view
        dimetric_loc: Tuple[float, float, float] = calculate_dimetric_angle(l=12, reference=CENTER)
        self.camera.setPos(*dimetric_loc)
        self.camera.lookAt(*CENTER)


        #self.camLens.setNearFar(1.0, 50.0)
        self.camLens.setFov(90.0)
        # Tilt the camera down by setting its pitch.
        #self.camera.setP(-90)

    def _init_lighting(self):
        """Set up lighting of scene."""
        self.ambientLight = self.render.attachNewNode(
            AmbientLight("ambient light")
        )
        self.ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.render.setLight(self.ambientLight)

        self.mainLight = self.render.attachNewNode(
            DirectionalLight("main light")
        )
        # Turn it around by 45 degrees, and tilt it down by 45 degrees
        #self.mainLight.setHpr(45, -45, 0)
        self.mainLight.setHpr(60, -30, 0)
        self.render.setLight(self.mainLight)

    def _init_keys(self):
        """Configure key mapping."""
        self.accept("d", self.move_camera, [1.0, 0.0, 0.0])
        self.accept("a", self.move_camera, [-1.0, 0.0, 0.0])
        self.accept("w", self.move_camera, [0.0, 1.0, 0.0])
        self.accept("s", self.move_camera, [0.0, -1.0, 0.0])
        self.accept("e", self.move_camera, [0.0, 0.0, 1.0])
        self.accept("q", self.move_camera, [0.0, 0.0, -1.0])

    def _init_graphics(self):
        """Configure graphics."""
        pass

    def move_camera(self, x, y, z):
        """Helper function to move camera."""
        self.camera.setX(self.camera.getX() + x)
        self.camera.setY(self.camera.getY() + y)
        self.camera.setZ(self.camera.getZ() + z)

    def paint_playground(self):
        """
        Draw playground, and add players/spores onto it.
        """
        # setup background
        self.set_background_color(pColor(visual_cfg.stage_background))

        # make the main board on which players stand
        scalar: float = 1.
        playground_color: Tuple[int, int, int] = pColor(
            map_ref[101][-1]
        )

        playboard_gn: GeomNode = make_a_cuboid(*self.pg_size)
        self.playboard = self.render.attachNewNode(playboard_gn)
        self.playboard.setTwoSided(True)
        self.playboard.setPos(0, 0, 0)
        self.playboard.setScale(scalar, scalar, scalar)
        self.playboard.setColor(*playground_color)

    def _figure_out_multiplier(self):
        """Helper function to calculate mapping values."""
        self.cube_x = self.pg_size[0] / self.bitmap.shape[0]
        self.cube_y = self.pg_size[1] / self.bitmap.shape[1]
        
    def map_bitmap_loc_to_playboard_loc(
            self, bitmap_x: int, bitmap_y: int
        ) -> Tuple[float, float]:
        """
        Map locations on bitmap to playground.
        Some offset are added because (0, 0) on bitmap is actually the upper
        left cornor on playground.
        """
        # x and y shifts, types are floats
        x_shift, y_shift = self.pg_size[0] / 2 , self.pg_size[1] / 2
        
        board_x: float = bitmap_x * self.cube_x - x_shift + self.cube_x / 2
        board_y: float = bitmap_y * self.cube_y - y_shift + self.cube_y / 2

        return board_x, board_y

    def add_cube(
            self,
            ref: NodePath = None,
            loc: Tuple[int, int] = (0, 0),
            color: Tuple[float, float, float, float] = (1., 0., 0., 1.),
            z_shift: float = None,
        ) -> NodePath:
        """
        Add a single cube/cuboid onto playground.
        
        Args
            ref: Root object to which the cube to attach.
            loc: Coor of the cube on bitmap; NOT on the reference.
            z_shift: Usually positve, such that the cube would appear to be
                sitting above the playground. If None was given, it will use
                height of playground so that cubes will be right above board.

        Returns
            NodePath: Object pointer.
        """
        # if reference object is None, then use the render itself as root
        if ref is None:
            ref = self.render
        if z_shift is None:  # set height shift if None was given
            # half of playboard height because by default, playboard is set to the
            # very center of scene, namely, (0, 0, 0) and therefore on each dimension
            # length is halved (half above 0 and the other halve below 0)
            z_shift = self.pg_size[-1] / 2

        # scalar of cube, maybe it's not needed but I will leave it for potential
        # future uses
        scalar: float = 1.

        # map bitmap location to playboard, types are floats
        loc_x, loc_y = self.map_bitmap_loc_to_playboard_loc(*loc)

        # make a cube or cuboid
        if self.cube_x == self.cube_y:
            snode: GeomNode = make_a_cube(self.cube_x)
        else:
            snode = make_a_cuboid(self.cube_x, self.cube_y, self.cube_z)
        # attach cube to the reference object
        cube: NodePath = ref.attachNewNode(snode)
        # OpenGl by default only draws "front faces" (polygons whose vertices are
        # specified CCW).
        cube.setTwoSided(True)
        cube.setPos(loc_x, loc_y, z_shift)

        if scalar != 1.:  # rescale the cube if a scalar was specified
            cube.setScale(scalar, scalar, scalar)

        # test color setup
        #c: Tuple[int, int, int] = 
        cube.setColor(*color)
        return cube

    def remove_spore_by_id(self, spore_id: int):
        """Remove a NodePath representitive of a spore by using its id."""
        spore_np: NodePath = self.spore_tracker[spore_id]
        spore_np.detachNode()

    def add_cube_by_spore(            
            self,
            spore: Spore,
            ref: NodePath = None,
            z_shift: float = None
        ):
        """Wrapper of add_cube() but with a Spore object."""
        loc: Tuple[int, int] = spore.pos

        color: Tuple[float, ...] = pColor(map_ref[spore.sex][-1])
        cube: NodePath = self.add_cube(ref=ref, loc=loc, color=color, z_shift=z_shift)
        self.spore_tracker[spore.sid] = cube

    def add_initial_players(self):
        """Add inital batch of spores."""
        # if colony for some reason was not parse, then place four cubes on
        # four corners (indicating it's empty)
        if self.colony is None:
            top_x: int = self.bitmap.shape[0]
            top_y: int = self.bitmap.shape[1]
            
            self.add_cube(ref=self.playboard, loc=(top_x, top_y))
            self.add_cube(ref=self.playboard, loc=(0, 0))
            self.add_cube(ref=self.playboard, loc=(0, top_y))
            self.add_cube(ref=self.playboard, loc=(top_x, 0))
            return
        
        spore_man: ColonySporeManager = self.colony.spore_man
        for _, spore in spore_man.spores.items():
            self.add_cube_by_spore(spore, ref=self.playboard)


if __name__ == "__main__":
    panda_viewer: PandaViewer = PandaViewer()
    panda_viewer.run()