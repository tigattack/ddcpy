import re
import shutil
import subprocess
from typing import Union


class M1DDCControl:
    def __init__(self):
        self.ddpath = self._find_m1ddc()

    def _find_m1ddc(self):
        m1ddc_path = shutil.which("m1ddc")
        if m1ddc_path:
            return m1ddc_path
        raise FileNotFoundError(
            "m1ddc command not found in PATH. Consider installing it " +
            "with 'brew install m1ddc'"
        )

    def _run_command(self, command: str):
        try:
            result = subprocess.run(
                [self.ddpath] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as exc:
            print(f"Error executing command: {exc}")
            return None

    def _get(self, display: Union[int, str], property_name: str):
        return self._run_command([
            "display",
            str(display),
            "get",
            property_name])

    def _get_max(self, display: Union[int, str], property_name: str):
        result = self._run_command([
            "display",
            str(display),
            "max",
            property_name])
        return int(result)

    def _set(self, display: Union[int, str], property_name: str, value: Union[int, str]):
        return self._run_command(
            ["display", str(display), "set", property_name, str(value)]
        )

    def _change(self, display: Union[int, str], property_name: str, value: int):
        return self._run_command(
            ["display", str(display), "chg", property_name, str(value)]
        )

    def _parse_display_list(self, raw_output):
        display_list = []
        lines = raw_output.split("\n")
        for line in lines:
            match = re.match(r"^\[(\d+)\]\s+(.+?)\s+\(([\w-]+)\)$", line.strip())
            if match:
                display_number, display_name, display_id = match.groups()
                display_list.append(
                    {
                        "number": int(display_number),
                        "name": display_name,
                        "id": display_id,
                    }
                )
        return display_list

    def list_displays(self):
        raw_output = self._run_command(["display", "list"])
        if raw_output:
            return self._parse_display_list(raw_output)
        return []

    def get_luminance(self, display: Union[int, str]):
        return self._get(display, "luminance")

    def get_brightness(self, display: Union[int, str]):
        return self.get_luminance(display)

    def set_luminance(self, display: Union[int, str], value: int):
        max_value = self.max_luminance(display)
        if value < 0 or value > max_value:
            raise ValueError(f"Luminance value must be between 0 and {max_value}")
        return self._set(display, "luminance", value)

    def set_brightness(self, display: Union[int, str], value: int):
        return self.set_luminance(display, value)

    def get_contrast(self, display: Union[int, str]):
        return self._get(display, "contrast")

    def set_contrast(self, display: Union[int, str], value: int):
        max_value = self.max_contrast(display)
        if value < 0 or value > max_value:
            raise ValueError(f"Contrast value must be between 0 and {max_value}")
        return self._set(display, "contrast", value)

    def get_input(self, display: Union[int, str]):
        return self._get(display, "input")

    def set_input(self, display: Union[int, str], value: int):
        return self._set(display, "input", value)

    def get_volume(self, display: Union[int, str]):
        return self._get(display, "volume")

    def set_volume(self, display: Union[int, str], value: int):
        max_value = self.max_volume(display)
        if value < 0 or value > max_value:
            raise ValueError(f"Volume value must be between 0 and {max_value}")

        return self._set(display, "volume", value)

    def set_mute(self, display: Union[int, str], state: bool = True):
        mute_state = "on" if state else "off"
        return self._set(display, "mute", mute_state)

    def max_luminance(self, display: Union[int, str]):
        return self._get_max(display, "luminance")

    def max_contrast(self, display: Union[int, str]):
        return self._get_max(display, "contrast")

    def max_volume(self, display: Union[int, str]):
        return self._get_max(display, "volume")

    def change_luminance(self, display: Union[int, str], value: int):
        current_value = self.get_luminance(display)
        max_value = self.max_luminance(display)
        try:
            if value + current_value < 0 or value + current_value > max_value:
                raise ValueError(
                    f"Luminance value must be between 0 and {max_value}. " +
                    "Requested result {value + current_value} is out of range."
                )
            return self._change(display, "luminance", value)
        except ValueError as exc:
            print(f"Error changing luminance: {exc}")

    def change_contrast(self, display: Union[int, str], value: int):
        current_value = self.get_contrast(display)
        max_value = self.max_contrast(display)
        try:
            if value + current_value < 0 or value + current_value > max_value:
                raise ValueError(
                    f"Contrast value must be between 0 and {max_value}. " +
                    "Requested result {value + current_value} is out of range."
                )
            return self._change(display, "contrast", value)
        except ValueError as exc:
            print(f"Error changing contrast: {exc}")

    def change_volume(self, display: Union[int, str], value: int):
        current_value = self.get_volume(display)
        max_value = self.max_volume(display)
        try:
            if value + current_value < 0 or value + current_value > max_value:
                raise ValueError(
                    f"Volume value must be between 0 and {max_value}. " +
                    "Requested result {value + current_value} is out of range."
                )
            return self._change(display, "volume", value)
        except ValueError as exc:
            print(f"Error changing volume: {exc}")
