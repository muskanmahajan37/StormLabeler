"""Captures polygons drawn by a human over a pre-existing image.

NOTE: This script is interactive and requires an interactive display.  You
cannot run it on a supercomputer without X-forwarding or whatever it's called.
"""

import argparse
from stormlabeler.utils import human_polygons

IMAGE_FILE_ARG_NAME = 'input_image_file_name'
POS_NEG_ARG_NAME = 'positive_and_negative'
NUM_GRID_ROWS_ARG_NAME = 'num_grid_rows'
NUM_GRID_COLUMNS_ARG_NAME = 'num_grid_columns'
NUM_PANEL_ROWS_ARG_NAME = 'num_panel_rows'
NUM_PANEL_COLUMNS_ARG_NAME = 'num_panel_columns'
OUTPUT_FILE_ARG_NAME = 'output_file_name'

IMAGE_FILE_HELP_STRING = (
    'Path to input file.  Polygons will be drawn over this image.')

POS_NEG_HELP_STRING = (
    'Boolean flag.  If 1, will capture positive and negative polygons (regions '
    'where the quantity of interest is strongly positive and negative, '
    'respectively).  If 0, will capture only positive polygons.')

NUM_GRID_ROWS_HELP_STRING = (
    'Number of rows in grid.  This method assumes that the image contains one '
    'or more panels with gridded data.')

NUM_GRID_COLUMNS_HELP_STRING = (
    'Number of columns in grid.  This method assumes that the image contains '
    'one or more panels with gridded data.')

NUM_PANEL_ROWS_HELP_STRING = (
    'Number of panel rows in image.  Each panel may contain a different '
    'variable, but they must all contain the same grid, with the same aspect '
    'ratio and no whitespace border (between the panels or around the outside '
    'of the image).')

NUM_PANEL_COLUMNS_HELP_STRING = 'Number of panel columns in image.'

OUTPUT_FILE_HELP_STRING = (
    'Path to output file.  Will be written by `human_polygons.write_polygons`.')

INPUT_ARG_PARSER = argparse.ArgumentParser()
INPUT_ARG_PARSER.add_argument(
    '-i', '--' + IMAGE_FILE_ARG_NAME, type=str, required=True,
    help=IMAGE_FILE_HELP_STRING)

INPUT_ARG_PARSER.add_argument(
    '-posandneg', '--' + POS_NEG_ARG_NAME, type=int, required=False, default=0,
    help=POS_NEG_HELP_STRING)

INPUT_ARG_PARSER.add_argument(
    '-ngridrows', '--' + NUM_GRID_ROWS_ARG_NAME, type=int, required=True,
    help=NUM_GRID_ROWS_HELP_STRING)

INPUT_ARG_PARSER.add_argument(
    '-ngridcols', '--' + NUM_GRID_COLUMNS_ARG_NAME, type=int, required=True,
    help=NUM_GRID_COLUMNS_HELP_STRING)

INPUT_ARG_PARSER.add_argument(
    '-npanelrows', '--' + NUM_PANEL_ROWS_ARG_NAME, type=int, required=True,
    help=NUM_PANEL_ROWS_HELP_STRING)

INPUT_ARG_PARSER.add_argument(
    '-npanelcols', '--' + NUM_PANEL_COLUMNS_ARG_NAME, type=int, required=True,
    help=NUM_PANEL_COLUMNS_HELP_STRING)

INPUT_ARG_PARSER.add_argument(
    '-o', '--' + OUTPUT_FILE_ARG_NAME, type=str, required=True,
    help=OUTPUT_FILE_HELP_STRING)


def _run(input_image_file_name, positive_and_negative, num_grid_rows,
         num_grid_columns, num_panel_rows, num_panel_columns, output_file_name):
    """Captures polygons drawn by a human over a pre-existing image.

    This is effectively the main method.

    :param input_image_file_name: See documentation at top of file.
    :param positive_and_negative: Same.
    :param num_grid_rows: Same.
    :param num_grid_columns: Same.
    :param num_panel_rows: Same.
    :param num_panel_columns: Same.
    :param output_file_name: Same.
    """

    positive_objects_pixel_coords, num_pixel_rows, num_pixel_columns = (
        human_polygons.capture_polygons(
            image_file_name=input_image_file_name,
            instruction_string='Outline POSITIVE regions of interest.')
    )

    (positive_objects_grid_coords, positive_panel_row_by_polygon,
     positive_panel_column_by_polygon
    ) = human_polygons.polygons_from_pixel_to_grid_coords(
        polygon_objects_pixel_coords=positive_objects_pixel_coords,
        num_grid_rows=num_grid_rows, num_grid_columns=num_grid_columns,
        num_pixel_rows=num_pixel_rows, num_pixel_columns=num_pixel_columns,
        num_panel_rows=num_panel_rows, num_panel_columns=num_panel_columns)

    positive_mask_matrix = human_polygons.polygons_to_mask(
        polygon_objects_grid_coords=positive_objects_grid_coords,
        num_grid_rows=num_grid_rows, num_grid_columns=num_grid_columns,
        num_panel_rows=num_panel_rows, num_panel_columns=num_panel_columns,
        panel_row_by_polygon=positive_panel_row_by_polygon,
        panel_column_by_polygon=positive_panel_column_by_polygon)

    if positive_and_negative:
        negative_objects_pixel_coords, num_pixel_rows, num_pixel_columns = (
            human_polygons.capture_polygons(
                image_file_name=input_image_file_name,
                instruction_string='Outline NEGATIVE regions of interest.')
        )

        (negative_objects_grid_coords, negative_panel_row_by_polygon,
         negative_panel_column_by_polygon
        ) = human_polygons.polygons_from_pixel_to_grid_coords(
            polygon_objects_pixel_coords=negative_objects_pixel_coords,
            num_grid_rows=num_grid_rows, num_grid_columns=num_grid_columns,
            num_pixel_rows=num_pixel_rows, num_pixel_columns=num_pixel_columns,
            num_panel_rows=num_panel_rows, num_panel_columns=num_panel_columns)

        negative_mask_matrix = human_polygons.polygons_to_mask(
            polygon_objects_grid_coords=negative_objects_grid_coords,
            num_grid_rows=num_grid_rows, num_grid_columns=num_grid_columns,
            num_panel_rows=num_panel_rows, num_panel_columns=num_panel_columns,
            panel_row_by_polygon=negative_panel_row_by_polygon,
            panel_column_by_polygon=negative_panel_column_by_polygon)
    else:
        negative_objects_grid_coords = None
        negative_panel_row_by_polygon = None
        negative_panel_column_by_polygon = None
        negative_mask_matrix = None

    print('Writing polygons and masks to: "{0:s}"...'.format(output_file_name))

    human_polygons.write_polygons(
        output_file_name=output_file_name,
        orig_image_file_name=input_image_file_name,
        positive_objects_grid_coords=positive_objects_grid_coords,
        positive_panel_row_by_polygon=positive_panel_row_by_polygon,
        positive_panel_column_by_polygon=positive_panel_column_by_polygon,
        positive_mask_matrix=positive_mask_matrix,
        negative_objects_grid_coords=negative_objects_grid_coords,
        negative_panel_row_by_polygon=negative_panel_row_by_polygon,
        negative_panel_column_by_polygon=negative_panel_column_by_polygon,
        negative_mask_matrix=negative_mask_matrix)


if __name__ == '__main__':
    INPUT_ARG_OBJECT = INPUT_ARG_PARSER.parse_args()

    _run(
        input_image_file_name=getattr(INPUT_ARG_OBJECT, IMAGE_FILE_ARG_NAME),
        positive_and_negative=bool(getattr(
            INPUT_ARG_OBJECT, POS_NEG_ARG_NAME
        )),
        num_grid_rows=getattr(INPUT_ARG_OBJECT, NUM_GRID_ROWS_ARG_NAME),
        num_grid_columns=getattr(INPUT_ARG_OBJECT, NUM_GRID_COLUMNS_ARG_NAME),
        num_panel_rows=getattr(INPUT_ARG_OBJECT, NUM_PANEL_ROWS_ARG_NAME),
        num_panel_columns=getattr(INPUT_ARG_OBJECT, NUM_PANEL_COLUMNS_ARG_NAME),
        output_file_name=getattr(INPUT_ARG_OBJECT, OUTPUT_FILE_ARG_NAME)
    )
