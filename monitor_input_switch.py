#!/usr/bin/env python3
"""Script to control monitors with DDC-CI"""

import argparse
import logging
import sys
from time import sleep

from m1ddc.m1ddc import M1DDCControl


# Define inputs
INPUTS = {
    'hdmi': 17,
    'usbc': 49
}

# Define display settings for each machine
MACHINE_CONFS = {
    'work': {
        'input': INPUTS['hdmi'],
        'contrast': 75
    },
    'mac': {
        'input': INPUTS['usbc'],
        'contrast': 75
    }
}

# Configure logging
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Set input and contrast for displays.")
    parser.add_argument(
        "target_machine",
        choices=["work", "mac", "swap"],
        help="Choose an available machine or swap between them",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    return parser.parse_args()


def configure_logging(debug):
    """Configure logging based on debug mode."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)
    return logging.getLogger(__name__)


def determine_display_settings(machine):
    """Determine display settings based on the target machine."""

    if machine not in MACHINE_CONFS:
        logger.error(f"Unrecognised machine: {machine}")
        sys.exit(1)

    display_settings = MACHINE_CONFS[machine]
    input_name = next(
        (
            key
            for key, value in INPUTS.items()
            if value == display_settings["input"]
        ),
        None,
    )
    logger.debug(
        f'Determined input should be set to {input_name} ({display_settings["input"]})'
    )
    logger.debug(
        f'Determined contrast should be set to {display_settings["contrast"]}'
    )

    return display_settings


def check_display_readiness(m1ddc, display_id):
    """Check if the display is ready to accept further commands."""
    logger.debug(
        "Attempting to get the first display's maximum contrast until non-zero value is returned."
    )
    logger.debug(
        "This tests the readiness of the display(s) to accept further commands."
    )
    logger.debug("Checking display readiness...")
    max_contrast = 0
    checks = 0
    while max_contrast == 0:
        sleep(0.75)
        logger.debug("Checking display readiness...")
        max_contrast = m1ddc.max_contrast(display_id)
        checks += 1
        if checks > 10:
            logger.error("Timed out waiting for non-zero contrast value.")
            sys.exit(1)


def set_display_input(m1ddc, displays, input_value):
    for display in displays:
        logger.debug(
            f"Setting display {display['number']} to input {input_value}")
        m1ddc.set_input(display["id"], input_value)


def set_display_contrast(m1ddc, displays, contrast_value):
    for display in displays:
        logger.debug(f"Setting display {display['number']} contrast to {contrast_value}")
        m1ddc.set_contrast(display["id"], contrast_value)


def swap_targets(m1ddc, displays):
    for display in displays:
        logger.debug(f"Swapping display {display['number']}")
        m1ddc.get_input(display["id"])
        if display["input"] == INPUTS["hdmi"]:
            m1ddc.set_input(display["id"], INPUTS["usbc"])
        elif display["input"] == INPUTS["usbc"]:
            m1ddc.set_input(display["id"], INPUTS["hdmi"])
        else:
            logger.error(f"Current input unrecognised: {display['input']}")
            sys.exit(1)


def main():
    """Main function to set input and contrast for displays."""
    args = parse_args()
    target_machine = args.target_machine.lower()

    # Configure logging
    configure_logging(args.debug)

    # Create an instance of M1DDCControl
    m1ddc = M1DDCControl()

    # Retrieve the list of displays and count them
    displays = m1ddc.list_displays()
    num_displays = len(displays)

    # Check if any displays are found
    if num_displays < 1:
        logger.error("No displays found or an error occurred.")
        sys.exit(1)

    logger.debug(f"Found {num_displays} displays")

    # Determine display settings based on the target machine
    display_settings = determine_display_settings(target_machine)

    # Set display input
    set_display_input(m1ddc, displays, display_settings["input"])

    # Check display readiness
    check_display_readiness(m1ddc, displays[0]["id"])

    # Set display contrast
    set_display_contrast(m1ddc, displays, display_settings["contrast"])

    logger.info(f"Set input and contrast for {num_displays} display.")


if __name__ == "__main__":
    main()
