import questionary
from typing import Optional, Dict, Any
from ..models.bangle import BangleSpec
from ..core.discovery import SizingStockLookup
from ..config.settings import BanglerConfig

class BanglePrompter:
    """Guided prompts for bangle specification collection"""

    def __init__(self):
        self.sizing_stock = SizingStockLookup()
        self.rules = BanglerConfig.BUSINESS_RULES
        # Navigation state
        self.BACK_OPTION = "← Back"
        self.current_spec = {}

    def prompt_size(self) -> Optional[int]:
        """Step 1: Size selection (10-27)"""
        size_choices = [str(i) for i in range(self.rules['min_size'], self.rules['max_size'] + 1)]

        try:
            size_str = questionary.select(
                "Select bangle size:",
                choices=size_choices,
                instruction="(Size determines the inside diameter of the bangle)"
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise KeyboardInterrupt()

        return int(size_str)

    def prompt_metal_shape(self) -> Optional[str]:
        """Step 2: Metal Shape selection"""
        choices = self.rules['valid_shapes'] + [self.BACK_OPTION]

        try:
            shape = questionary.select(
                "Select metal shape:",
                choices=choices,
                instruction="(Shape affects available width and thickness options)"
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise KeyboardInterrupt()

        if shape == self.BACK_OPTION:
            return "BACK"

        return shape

    def prompt_metal_color(self) -> Optional[str]:
        """Step 3: Metal Color selection"""
        color_choices = list(self.rules['valid_colors']) + [self.BACK_OPTION]

        try:
            color = questionary.select(
                "Select metal color:",
                choices=color_choices,
                instruction="(Sterling Silver skips quality selection)"
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise KeyboardInterrupt()

        if color == self.BACK_OPTION:
            return "BACK"

        return color

    def prompt_metal_quality(self, color: str) -> Optional[str]:
        """Step 4: Metal Quality selection (skipped if Sterling Silver)"""
        if color in ["Sterling Silver", "Continuum Sterling Silver"]:
            return None

        # Get dynamic quality options from CSV data
        available_options = self.sizing_stock.get_available_options()
        quality_options = [q for q in available_options['qualities'] if color.lower() in q.lower()]

        if not quality_options:
            # Fallback to hardcoded if no matches found
            quality_options = self.rules['valid_qualities']

        quality_options.append(self.BACK_OPTION)

        try:
            quality = questionary.select(
                f"Select {color} gold quality:",
                choices=quality_options,
                instruction="(Higher karat = more gold content = higher cost)"
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise KeyboardInterrupt()

        if quality == self.BACK_OPTION:
            return "BACK"

        return quality

    def prompt_width(self, shape: str, quality_string: str) -> Optional[str]:
        """Step 5: Width selection (filtered by shape)"""
        available_options = self.sizing_stock.get_nested_options_for_cli()

        if shape not in available_options:
            raise ValueError(f"No options available for shape: {shape}")

        # Get unique widths for this shape and quality
        shape_data = available_options[shape]
        available_widths = set()

        if quality_string in shape_data:
            available_widths.update(shape_data[quality_string].keys())

        if not available_widths:
            raise ValueError(f"No widths available for {shape} {quality_string}")

        width_choices = sorted(available_widths, key=lambda x: float(x.replace(' Mm', '')))
        width_choices.append(self.BACK_OPTION)

        try:
            width = questionary.select(
                f"Select width for {shape} {quality_string}:",
                choices=width_choices,
                instruction="(Width affects the bangle's appearance and material cost)"
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise KeyboardInterrupt()

        if width == self.BACK_OPTION:
            return "BACK"

        return width

    def prompt_thickness(self, shape: str, quality_string: str, width: str) -> Optional[str]:
        """Step 6: Thickness selection (filtered by shape and width)"""
        available_options = self.sizing_stock.get_nested_options_for_cli()

        # Navigate to thickness options
        try:
            thickness_options = available_options[shape][quality_string][width]
        except KeyError:
            raise ValueError(f"No thickness options for {shape} {quality_string} {width}")

        thickness_choices = sorted(thickness_options, key=lambda x: float(x.replace(' Mm', '')))
        thickness_choices.append(self.BACK_OPTION)

        try:
            thickness = questionary.select(
                f"Select thickness for {shape} {quality_string} {width}:",
                choices=thickness_choices,
                instruction="(Thickness affects strength and material needed)"
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise KeyboardInterrupt()

        if thickness == self.BACK_OPTION:
            return "BACK"

        return thickness

    def collect_complete_specification(self) -> Optional[BangleSpec]:
        """Complete guided workflow to collect all bangle specifications with Back navigation"""
        print("\n=== Bangle Pricing Calculator ===")
        print("Let's gather the specifications for your custom bangle.\n")

        # State machine for navigation
        step = 1
        self.current_spec = {}

        while True:
            try:
                if step == 1:
                    # Step 1: Size
                    result = self.prompt_size()
                    if result is not None:
                        self.current_spec['size'] = result
                        print(f"✓ Size: {result}")
                        step = 2
                    else:
                        return None  # User cancelled

                elif step == 2:
                    # Step 2: Metal Shape
                    result = self.prompt_metal_shape()
                    if result == "BACK":
                        step = 1
                        continue
                    elif result is not None:
                        self.current_spec['metal_shape'] = result
                        print(f"✓ Shape: {result}")
                        step = 3
                    else:
                        return None  # User cancelled

                elif step == 3:
                    # Step 3: Metal Color
                    result = self.prompt_metal_color()
                    if result == "BACK":
                        step = 2
                        continue
                    elif result is not None:
                        self.current_spec['metal_color'] = result
                        print(f"✓ Color: {result}")
                        step = 4
                    else:
                        return None  # User cancelled

                elif step == 4:
                    # Step 4: Metal Quality (conditional)
                    result = self.prompt_metal_quality(self.current_spec['metal_color'])
                    if result == "BACK":
                        step = 3
                        continue
                    elif result is not None or self.current_spec['metal_color'] in ["Sterling Silver", "Continuum Sterling Silver"]:
                        self.current_spec['metal_quality'] = result
                        if result:
                            print(f"✓ Quality: {result}")
                        else:
                            print("✓ Quality: Sterling Silver (no karat selection needed)")
                        step = 5
                    else:
                        return None  # User cancelled

                elif step == 5:
                    # Step 5: Width (filtered by shape)
                    # Handle quality string construction - CSV data may already include color
                    if self.current_spec['metal_quality']:
                        # If quality already contains the color, use it as-is, otherwise combine
                        if self.current_spec['metal_color'].lower() in self.current_spec['metal_quality'].lower():
                            quality_string = self.current_spec['metal_quality']
                        else:
                            quality_string = f"{self.current_spec['metal_quality']} {self.current_spec['metal_color']}"
                    else:
                        quality_string = self.current_spec['metal_color']
                    try:
                        result = self.prompt_width(self.current_spec['metal_shape'], quality_string)
                        if result == "BACK":
                            step = 4
                            continue
                        elif result is not None:
                            self.current_spec['width'] = result
                            print(f"✓ Width: {result}")
                            step = 6
                        else:
                            return None  # User cancelled
                    except ValueError as e:
                        print(f"\n❌ {e}")
                        self._show_available_alternatives(self.current_spec['metal_shape'], quality_string)
                        print("\nPlease go back and try a different combination.")
                        step = 4  # Go back to quality selection
                        continue

                elif step == 6:
                    # Step 6: Thickness (filtered by shape and width)
                    # Handle quality string construction - CSV data may already include color
                    if self.current_spec['metal_quality']:
                        # If quality already contains the color, use it as-is, otherwise combine
                        if self.current_spec['metal_color'].lower() in self.current_spec['metal_quality'].lower():
                            quality_string = self.current_spec['metal_quality']
                        else:
                            quality_string = f"{self.current_spec['metal_quality']} {self.current_spec['metal_color']}"
                    else:
                        quality_string = self.current_spec['metal_color']
                    try:
                        result = self.prompt_thickness(self.current_spec['metal_shape'], quality_string, self.current_spec['width'])
                        if result == "BACK":
                            step = 5
                            continue
                        elif result is not None:
                            self.current_spec['thickness'] = result
                            print(f"✓ Thickness: {result}")
                            break  # All steps complete
                        else:
                            return None  # User cancelled
                    except ValueError as e:
                        print(f"\n❌ {e}")
                        self._show_thickness_alternatives(self.current_spec['metal_shape'], quality_string, self.current_spec['width'])
                        print("\nPlease go back and try a different combination.")
                        step = 5  # Go back to width selection
                        continue

            except KeyboardInterrupt:
                # Let KeyboardInterrupt propagate to exit the program
                raise

        # Create and return complete specification
        spec = BangleSpec(
            size=self.current_spec['size'],
            metal_shape=self.current_spec['metal_shape'],
            metal_color=self.current_spec['metal_color'],
            metal_quality=self.current_spec['metal_quality'],
            width=self.current_spec['width'],
            thickness=self.current_spec['thickness']
        )

        print("\n=== Specification Complete ===")
        print(f"Size: {spec.size}")
        print(f"Metal: {spec.to_quality_string()}")
        print(f"Shape: {spec.metal_shape}")
        print(f"Dimensions: {spec.width} x {spec.thickness}")
        print("=" * 30)

        return spec

    def _show_available_alternatives(self, shape: str, quality_string: str) -> None:
        """Show available alternatives for shape/quality combination"""
        available_options = self.sizing_stock.get_nested_options_for_cli()
        try:
            if shape in available_options and quality_string in available_options[shape]:
                # This shouldn't happen if we reach this method, but just in case
                available_widths = list(available_options[shape][quality_string].keys())
                print(f"\n💡 Available widths for {shape} {quality_string}:")
                for width_option in available_widths:
                    print(f"   • {width_option}")
            elif shape in available_options:
                # Shape exists but quality doesn't - show available qualities
                available_qualities = list(available_options[shape].keys())
                print(f"\n💡 The quality '{quality_string}' is not available for {shape}.")
                print(f"   Available qualities for {shape}:")
                for quality in available_qualities:
                    print(f"   • {quality}")
            else:
                # Shape doesn't exist - show available shapes
                print(f"\n💡 The shape '{shape}' is not available.")
                print(f"   Available shapes:")
                for shape_option in available_options.keys():
                    print(f"   • {shape_option}")
        except KeyError:
            print(f"\n💡 This combination may not be available. Please try different selections.")

    def _show_thickness_alternatives(self, shape: str, quality_string: str, width: str) -> None:
        """Show available thickness alternatives"""
        available_options = self.sizing_stock.get_nested_options_for_cli()
        try:
            available_thicknesses = available_options[shape][quality_string][width]
            print(f"\n💡 Available thicknesses for {shape} {quality_string} {width}:")
            for thickness_option in available_thicknesses:
                print(f"   • {thickness_option}")
        except KeyError:
            try:
                available_widths = list(available_options[shape][quality_string].keys())
                print(f"\n💡 Available widths for {shape} {quality_string}:")
                for w in available_widths:
                    print(f"   • {w}")
            except KeyError:
                print(f"\n💡 This combination may not be available. Please try different selections.")