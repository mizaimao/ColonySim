"""Painter functions to draw 2D or isometric views of upper panel.
"""
from typing import Dict, List, Tuple, Union
import cv2
import numpy as np
from math import sqrt

from colony.configs.map_generator.ref import map_ref
from colony.utils.color_helpers import shift_color
from colony.utils.image_manager import ImageManager
from colony.vis.colony_viewers_basic import ColonyView, STAGE_BACKGROUND


# left blank spaces of upper and lower frame
ISO_UPPER: float = 0.05  # ratio to frame height
ISO_LOWER: float = 0.05

ISO_TILE_WIDTH_SCALAR: float = sqrt(3)
ISO_TILE_HEIGHT_SCALAR: float = 1.0
ISO_TILE_UPPER_THICKNESS_SCALAR: float = .5  # ratio to tile height
ISO_TILE_LOWER_THICKNESS_SCALAR: float = 2.

ISO_TILE_UPPER_LEFT_COLOR_SHIFT: Union[int, Tuple[int, ...]] = -40
ISO_TILE_UPPER_RIGHT_COLOR_SHIFT: Union[int, Tuple[int, ...]] = -20

ISO_TILE_GRID_LINE_THICKNESS: int = 4
ISO_TILE_OUTLINE_THICKNESS: int = 1
ISO_TILE_OUTLINE_COLOR: Tuple[float, ...] = (210,) * 3
ISO_TILE_LINE_COLOR: Tuple[float, ...] = (100, 100, 100)

DIRT_COLOR: Tuple[float, ...] = (83, 118, 155)  # BGR for sake of opencv


class ColonyViewIso(ColonyView):
    def __init__(
        self, width: int, height: int, frame_width: int, frame_height: int, bitmap
    ):
        assert (
            width == height
        ), f"Isometric view supports only square playground, got {(width, height)}"
        super().__init__(width, height, frame_width, frame_height, bitmap)

        # if colony shape is different from viewer shape, some spaces must be padded.
        self.left_blank: int = 0  # blank space on leftside
        self.top_blank: int = 0  # blank space on top

        # multiplier used for mapping isometric tile sizes
        self.multiplier_iso: float = 0

        # isometric tile shape (lenght of diagnoals, not sides of these dimond-shaped objects)
        self.tile_width: float = 0
        self.tile_height: float = 0

        # fake-3D gets a Z metric, some depth goes above a tile and the rest goes blow
        self.tile_upper_depth: float = 0
        self.tile_lower_depth: float = 0
        # offsets from edges, will be calculated later
        self.width_offset: float = 0
        self.height_offset: float = 0

        # figure out multiplier when projecting into isometric spaces
        self._figure_out_multiplier()

    def _figure_out_multiplier(self):
        """Here more than a simple multiplier was calculated. This is becasue the invovement of isometric mapping."""
        # this "traditional" multiplier set is used to scale UI stuffs, like it does in 2D version.
        multiplier_x: float = self.frame_width / self.width
        multiplier_y: float = self.frame_height / self.height
        self.multiplier = min(multiplier_x, multiplier_y)

        # this isotromic multiplier set is used to draw tiles
        # calculate artificial Y blanks, which are some reserved spaces at top and bottom (for fake hight in the future)
        deduced_y_space: float = self.frame_height * (ISO_UPPER + ISO_LOWER)
        multiplier_x_iso: float = self.frame_width / (
            self.width * ISO_TILE_WIDTH_SCALAR
        )
        multiplier_y_iso: float = (self.frame_height - deduced_y_space) / (
            self.height * ISO_TILE_HEIGHT_SCALAR
        )
        self.multiplier_iso = min(multiplier_x_iso, multiplier_y_iso)

        # calculate size of each tile. Not their sides but more like diagonals of the dimond shapes.
        self.tile_width = self.multiplier_iso * ISO_TILE_WIDTH_SCALAR
        self.tile_height = self.multiplier_iso * ISO_TILE_HEIGHT_SCALAR

        # figure out blank paddings at top and left
        self.left_blank = int((self.frame_width - self.tile_width * self.width) / 2)
        self.top_blank = int((self.frame_height - self.tile_height * self.height) / 2)

        # height offset is needed to "shift" pixles to right by half of playground width
        # different maths requires x-shifting, but it's not the case here
        self.width_offset = 0 + self.left_blank
        self.height_offset = self.tile_height * self.height / 2 + self.top_blank

        # figure out tile depth above and below surface
        # simple case now, just cut them into halves
        self.tile_upper_depth = self.tile_height * ISO_TILE_UPPER_THICKNESS_SCALAR
        self.tile_lower_depth = self.tile_height * ISO_TILE_LOWER_THICKNESS_SCALAR

    def _get_iso_coor(self, x: float, y: float):
        """Convert bitmap coordinates to isometric coordinates.
        OpenCV draw lines by using integer indices (of course).

        This projecting scheme makes dot (0, 0) or the upper left corner mapped to the very left spot.
        """
        # this isometric mapping requires y-shifting
        new_x: int = int(
            (x * self.tile_width / 2) + (y * self.tile_width / 2) + self.width_offset
        )
        new_y: int = int(
            (y * self.tile_height / 2) - (x * self.tile_height / 2) + self.height_offset
        )
        return (new_x, new_y)

    def _get_iso_coor_set(self, x: float, y: float) -> Tuple[Tuple[int, int], ...]:
        """Get projected four corners of a tile, that is,
        (x, x), (x + 1, y), (x + 1, y + 1) and (x, y + 1)
        """
        ul: Tuple[int, int] = self._get_iso_coor(x, y)
        ur: Tuple[int, int] = self._get_iso_coor(x + 1, y)
        ll: Tuple[int, int] = self._get_iso_coor(x, y + 1)
        lr: Tuple[int, int] = self._get_iso_coor(x + 1, y + 1)
        return (ul, ur, ll, lr)

    def _paint_grid_lines(self, frame: np.ndarray):
        """
        Draw grid lines for debugging purposes.
        """
        # add x grid lines to frame
        # from (0, Y0) to (x, Y0) until (0, Yy) to (x, Yy)
        for y in range(self.height + 1):
            start_point = self._get_iso_coor(0, y)
            end_point = self._get_iso_coor(self.width, y)
            cv2.line(
                frame,
                start_point,
                end_point,
                color=ISO_TILE_LINE_COLOR,
                thickness=ISO_TILE_GRID_LINE_THICKNESS,
            )
        # add y grid lines to frame
        # from (X0, 0) to (X0, y) until (Xx, 0) to (Xx, y)
        for x in range(self.width + 1):
            start_point = self._get_iso_coor(x, 0)
            end_point = self._get_iso_coor(x, self.height)
            cv2.line(
                frame,
                start_point,
                end_point,
                color=ISO_TILE_LINE_COLOR,
                thickness=ISO_TILE_GRID_LINE_THICKNESS,
            )

    def _paint_isometric_static_frame(self):
        # create a blank background
        frame = np.full(
            (self.frame_height, self.frame_width, 3), STAGE_BACKGROUND, dtype=np.uint8
        )
        return frame

    def get_static_frame(self):
        """Paint background and do essential calculations."""
        if self.static_frame is None:
            self.static_frame = self._paint_isometric_static_frame()
        return self.static_frame

    def paint_playground(self):
        """Paint the playground."""
        if self.static_frame is None:
            self.static_frame = self._paint_isometric_static_frame()

        # the loop order need to be modifed
        for y in range(len(self.bitmap)):
            for x in range(len(self.bitmap[0]) - 1, 0 - 1, -1):
                tile_painting_style: Union[str, Tuple[int, int, int]] = map_ref[self.bitmap[y][x]][-1]
                if isinstance(tile_painting_style, tuple):  # it's a color, then draw tile using this color
                    self.paint_large_pixel(self.static_frame, x, y, tile_painting_style, background=True)
                # elif isinstance(tile_painting_style, str):  
                # NOTE: there should be an offset to match tile offset when tile-drawing are not from images
                #     pass  # to be implemented
                else:
                    raise ValueError(f"Wrong type of drawing type: {type(tile_painting_style)}, \
                        check map_generator config file.")

    def paint_large_pixel_plane(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        """Draw mega pixel without depth info, just overlay them on a plane"""
        # the function adds blanks automatically
        # four corners of each tile
        ul, ur, ll, lr = self._get_iso_coor_set(x, y)
        contours = np.array([ul, ll, lr, ur])
        cv2.fillPoly(frame, pts=[contours], color=color)

    @staticmethod
    def draw_filled_polygon(
        frame: np.ndarray,
        contours: List[np.ndarray],
        color: Tuple[int, ...],
        outline_color: Tuple[int, ...] = None,
        outline_thickness: int = ISO_TILE_OUTLINE_THICKNESS):
        """Draw a polygon with color, as well as outline if supplied.
        Basically just combined two opencv functions."""
        cv2.fillPoly(frame, pts=[contours], color=color)
        if outline_color is not None:
            cv2.polylines(frame, pts=[contours], isClosed=True, color=outline_color, thickness=outline_thickness)

    def paint_large_pixel(
        self,
        frame: np.ndarray,
        x: int,
        y: int,
        color: Tuple,
        background: bool = False,
        outline: bool = True,
    ):
        """Draw mega pixles with depth inofmration. There will be five regions for each tile now.
        1. The surface of tile, which needs an Y offset to elevate from ground; we will use self.tile_upper_depth
        2. Elevated left side of a tile;
        3. Elevated right side of a tile;
        4. Underground left side of a tile; (only displays when x==0)
        5. Underground right side of a tile;  (only displays when y==Y)

        Background tiles are painted a bit differently:
        1. Depth are a bit shallower
        2. Only show depth when x==0 and y==Y

        Tile outline applies only to player/mimic/whatever-individual tiles, not backgrounds tiles.
        Some lines are overlapping. So different sides will have different number of line drawing statements.
        """
        upper_shifter: Tuple[int, int] = (0, int(self.tile_upper_depth))
        half_upper_shifter: Tuple[int, int] = (0, int(self.tile_upper_depth / 2))

        lower_shifter: Tuple[int, int] = (0, int(self.tile_lower_depth))
        half_lower_shifter: Tuple[int, int] = (0, int(self.tile_lower_depth / 2))

        if background:  # background has shallower depth (half of a tile)
            upper_shifter = half_upper_shifter
            half_upper_shifter = (0, 0)
            lower_shifter = half_lower_shifter
            half_lower_shifter = (0, 0)

        # four original corners of each tile
        ul, ur, ll, lr = self._get_iso_coor_set(x, y)

        # draw surface of a tile      ??? why a positive number causing it shift below ???
        contours: np.ndarray = np.array([ul, ll, lr, ur]) - upper_shifter
        self.draw_filled_polygon(frame, contours, color, ISO_TILE_OUTLINE_COLOR)

        # draw elevated left side
        if (not background) or (x == 0):
            contours = np.array([ul, ll, ll, ul]) - [upper_shifter, upper_shifter, half_upper_shifter, half_upper_shifter]
            self.draw_filled_polygon(
                frame,
                contours,
                shift_color(color, ISO_TILE_UPPER_LEFT_COLOR_SHIFT),
                ISO_TILE_OUTLINE_COLOR,
            )

        # draw elevated right side
        if (not background) or (y == self.height - 1):
            contours = np.array([ll, lr, lr, ll]) - [upper_shifter, upper_shifter, half_upper_shifter, half_upper_shifter]
            self.draw_filled_polygon(
                frame,
                contours,
                shift_color(color, ISO_TILE_UPPER_RIGHT_COLOR_SHIFT),
                ISO_TILE_OUTLINE_COLOR,
            )

        # # draw underground left side
        if background and (x == 0):
            contours = np.array([ul, ll, ll, ul]) + [lower_shifter, lower_shifter, half_lower_shifter, half_lower_shifter]
            self.draw_filled_polygon(
                frame,
                contours,
                shift_color(DIRT_COLOR, ISO_TILE_UPPER_LEFT_COLOR_SHIFT),
                ISO_TILE_OUTLINE_COLOR,
            )

        # draw underground right side
        if background and (y == self.height - 1):
            contours = np.array([ll, lr, lr, ll]) + [lower_shifter, lower_shifter, half_lower_shifter, half_lower_shifter]
            self.draw_filled_polygon(
                frame,
                contours,
                shift_color(DIRT_COLOR, ISO_TILE_UPPER_RIGHT_COLOR_SHIFT),
                ISO_TILE_OUTLINE_COLOR,
            )


class ColonyViewIsoImage(ColonyViewIso):
    """Extends the basic isometric viewer to support image overlaying.
    """
    def __init__(self, width: int, height: int, frame_width: int, frame_height: int, bitmap, seed: int = 42):
        """New attributes would be cached images or values will that will be repetitively calculated.
        """
        self.imager: ImageManager = ImageManager()
        self.rng = np.random.RandomState(seed)

        super().__init__(width, height, frame_width, frame_height, bitmap)

    @staticmethod
    def _add_alpha_if_necessary(image: np.ndarray):
        """Add one alpha channel (value==255) if necessary."""
        if image.shape[-1] == 3:  # three-channel image
            image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)  # it's BGR but whatever
        return image

    @staticmethod
    def _resize_image_by_width(image: np.ndarray, width: int):
        """Resize image with width while retaining aspect ratio."""
        org_h, org_w, _ = image.shape
        org_ratio: float = org_h / org_w
        return cv2.resize(image, (width, int(width * org_ratio)))

    def paint_floors(self, tiles: Union[np.ndarray, List[np.ndarray]]) -> np.ndarray:
        """Paint floors with a given tileset."""
        background: np.ndarray = self.static_frame.copy()
        
        if isinstance(tiles, np.ndarray):
            tiles = [tiles]
        indices: List[int] = self.rng.choice(len(tiles), self.bitmap.size)
        image_index: int = 0
        
        for y in range(len(self.bitmap)):
            for x in range(len(self.bitmap[0]) - 1, 0 - 1, -1):
                tile_image: np.ndarray = tiles[indices[image_index]]
                self.paint_image_as_large_pixel(background, x, y, tile_image)
                image_index += 1
                
        return background

    def paint_image_as_large_pixel(
        self,
        frame: np.ndarray,
        x: int,
        y: int,
        image: np.ndarray,
    ):
        """Paint a mega pixel from an image array.
        Caller need to accept a return value as the operation is not in-place.
        NOTE: I may messed up with what is x and what is y. Consequently, statements work but
        variables may not have correct names. lol.
        """
        # four original corners of each tile
        ul, ur, ll, lr = self._get_iso_coor_set(x, y)

        width: int = abs(ul[0] - lr[0])
        replace_y: int = ll[1]
        replace_x: int = lr[0]

        overlay_image = self._resize_image_by_width(image, width)
        img_height, img_width, _ = overlay_image.shape

        overlayed_part = frame[
            replace_y - img_height : replace_y, replace_x - img_width : replace_x
        ]
        # crop overlapping part and fill with zero for addition operation
        overlayed_part[np.where(overlay_image[:, :, 3] > 0)] = (0, 0, 0)
        # add overlaying image (but without alpha) to zero filled regions
        np.add(overlayed_part, overlay_image[:, :, :3], out=overlayed_part)

        # put the changed part back
        frame[
            replace_y - img_height : replace_y, replace_x - img_width : replace_x
        ] = overlayed_part
        return frame