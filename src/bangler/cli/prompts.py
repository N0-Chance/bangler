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

    def prompt_size(self) -> int:
        """Step 1: Size selection (10-27)"""
        size_choices = [str(i) for i in range(self.rules['min_size'], self.rules['max_size'] + 1)]

        size_str = questionary.select(
            "Select bangle size:",
            choices=size_choices,
            instruction="(Size determines the inside diameter of the bangle)"
        ).ask()

        # Handle Ctrl+C (returns None)
        if size_str is None:
            raise KeyboardInterrupt()

        return int(size_str)

    def prompt_metal_shape(self) -> str:
        """Step 2: Metal Shape selection"""
        shape = questionary.select(
            "Select metal shape:",
            choices=self.rules['valid_shapes'],
            instruction="(Shape affects available width and thickness options)"
        ).ask()

        # Handle Ctrl+C (returns None)
        if shape is None:
            raise KeyboardInterrupt()

        return shape

    def prompt_metal_color(self) -> str:
        """Step 3: Metal Color selection"""
        color = questionary.select(
            "Select metal color:",
            choices=self.rules['valid_colors'],
            instruction="(Sterling Silver skips quality selection)"
        ).ask()

        # Handle Ctrl+C (returns None)
        if color is None:
            raise KeyboardInterrupt()

        return color

    def prompt_metal_quality(self, color: str) -> Optional[str]:
        """Step 4: Metal Quality selection (skipped if Sterling Silver)"""
        if color == "Sterling Silver":
            return None

        quality = questionary.select(
            f"Select {color} gold quality:",
            choices=self.rules['valid_qualities'],
            instruction="(Higher karat = more gold content = higher cost)"
        ).ask()

        # Handle Ctrl+C (returns None)
        if quality is None:
            raise KeyboardInterrupt()

        return quality

    def prompt_width(self, shape: str, quality_string: str) -> str:
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

        width = questionary.select(
            f"Select width for {shape} {quality_string}:",
            choices=width_choices,
            instruction="(Width affects the bangle's appearance and material cost)"
        ).ask()

        # Handle Ctrl+C (returns None)
        if width is None:
            raise KeyboardInterrupt()

        return width

    def prompt_thickness(self, shape: str, quality_string: str, width: str) -> str:
        """Step 6: Thickness selection (filtered by shape and width)"""
        available_options = self.sizing_stock.get_nested_options_for_cli()

        # Navigate to thickness options
        try:
            thickness_options = available_options[shape][quality_string][width]
        except KeyError:
            raise ValueError(f"No thickness options for {shape} {quality_string} {width}")

        thickness_choices = sorted(thickness_options, key=lambda x: float(x.replace(' Mm', '')))

        thickness = questionary.select(
            f"Select thickness for {shape} {quality_string} {width}:",
            choices=thickness_choices,
            instruction="(Thickness affects strength and material needed)"
        ).ask()

        # Handle Ctrl+C (returns None)
        if thickness is None:
            raise KeyboardInterrupt()

        return thickness

    def collect_complete_specification(self) -> BangleSpec:
        """Complete guided workflow to collect all bangle specifications"""
        print("\n=== Bangle Pricing Calculator ===")
        print("Let's gather the specifications for your custom bangle.\n")

        # Step 1: Size
        size = self.prompt_size()
        print(f"✓ Size: {size}")

        # Step 2: Metal Shape
        metal_shape = self.prompt_metal_shape()
        print(f"✓ Shape: {metal_shape}")

        # Step 3: Metal Color
        metal_color = self.prompt_metal_color()
        print(f"✓ Color: {metal_color}")

        # Step 4: Metal Quality (conditional)
        metal_quality = self.prompt_metal_quality(metal_color)
        if metal_quality:
            print(f"✓ Quality: {metal_quality}")
        else:
            print("✓ Quality: Sterling Silver (no karat selection needed)")

        # Create quality string for lookup
        quality_string = f"{metal_quality} {metal_color}" if metal_quality else metal_color

        # Step 5: Width (filtered by shape)
        try:
            width = self.prompt_width(metal_shape, quality_string)
            print(f"✓ Width: {width}")
        except ValueError as e:
            print(f"\n❌ {e}")
            
            # Show available alternatives - widths for this shape/quality combination
            available_options = self.sizing_stock.get_nested_options_for_cli()
            try:
                if metal_shape in available_options and quality_string in available_options[metal_shape]:
                    available_widths = list(available_options[metal_shape][quality_string].keys())
                    print(f"\n💡 Available widths for {metal_shape} {quality_string}:")
                    for width_option in available_widths:  # Show all widths
                        print(f"   • {width_option}")
                elif metal_shape in available_options:
                    # Show available qualities for this shape if quality not found
                    available_qualities = list(available_options[metal_shape].keys())
                    print(f"\n💡 Available qualities for {metal_shape}:")
                    for quality in available_qualities:  # Show all qualities
                        print(f"   • {quality}")
                else:
                    # Show available shapes if shape not found
                    print(f"\n💡 Available shapes:")
                    for shape in available_options.keys():  # Show all shapes
                        print(f"   • {shape}")
            except KeyError:
                print(f"\n💡 This combination may not be available. Please try different selections.")
            
            print("\nPlease restart and try a different combination.")
            return None

        # Step 6: Thickness (filtered by shape and width)
        try:
            thickness = self.prompt_thickness(metal_shape, quality_string, width)
            print(f"✓ Thickness: {thickness}")
        except ValueError as e:
            print(f"\n❌ {e}")
            
            # Show available alternatives for this width
            available_options = self.sizing_stock.get_nested_options_for_cli()
            try:
                available_thicknesses = available_options[metal_shape][quality_string][width]
                print(f"\n💡 Available thicknesses for {metal_shape} {quality_string} {width}:")
                for thickness_option in available_thicknesses:  # Show all thicknesses
                    print(f"   • {thickness_option}")
            except KeyError:
                try:
                    available_widths = list(available_options[metal_shape][quality_string].keys())
                    print(f"\n💡 Available widths for {metal_shape} {quality_string}:")
                    for w in available_widths:  # Show all widths
                        print(f"   • {w}")
                except KeyError:
                    print(f"\n💡 This combination may not be available. Please try different selections.")
            
            print("\nPlease restart and try a different combination.")
            return None

        # Create and return complete specification
        spec = BangleSpec(
            size=size,
            metal_shape=metal_shape,
            metal_color=metal_color,
            metal_quality=metal_quality,
            width=width,
            thickness=thickness
        )

        print("\n=== Specification Complete ===")
        print(f"Size: {spec.size}")
        print(f"Metal: {spec.to_quality_string()}")
        print(f"Shape: {spec.metal_shape}")
        print(f"Dimensions: {spec.width} x {spec.thickness}")
        print("=" * 30)

        return spec